"""Integrating agronext_gis from a sale system: Triagem and Resolver, through the SDK.

One function per question the sale system asks. Every one takes the client as
its first argument and builds nothing, so exactly one place owns the client —
`gis_client`, an async generator:

* in a FastAPI app it is the dependency, as it stands:

      @router.post("/triagem")
      async def triagem(
          body: TriagemBody,
          gis: Annotated[gis_sdk.AgronextGisClient, Depends(gis_client)],
      ) -> TriagemAnswer:
          return to_answer(await run_triagem(gis, body.plots, product_id=body.product_id))

* in a script, `contextlib.asynccontextmanager(gis_client)()` — see `main`;
* in a test, hand the functions a client built on `httpx.MockTransport`.

Run it against an API (a key is minted in the UI: Usuários → chave de API):

    GIS_BASE_URL=http://localhost:8002 GIS_API_KEY=... \\
        uv run --with pydantic-settings python example.py

A plot is a GeoJSON Polygon or MultiPolygon in EPSG:4326, `[longitude, latitude]`
— never `[lat, lon]`. Every failure is a `gis_sdk.AgronextGisError`; a refusal
is an `ApiError` subclass whose `code` is what to branch on, never the wording.
"""

import asyncio
import contextlib
import functools
import logging
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal
from typing import Final

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

import agronext_gis_sdk as gis_sdk

logger = logging.getLogger("integrations.gis")

#: A GeoJSON Polygon or MultiPolygon, EPSG:4326.
type Plot = gis_sdk.GeoJson

#: The refusals of a resolve that are an ANSWER about the plot, not a failure:
#: part of it lies under the abrangência's proibida, or has no rate written.
#: `context` says how much and where (`unresolved_area_pct`, the cells).
FORBIDDEN_AREA: Final[str] = "rates.resolve.forbidden_area"
UNPRICED_AREA: Final[str] = "rates.resolve.unpriced_area"

#: The API's rate precision: six decimals, which every step of a rate rounds to.
RATE_QUANTUM: Final[Decimal] = Decimal("0.000001")

#: How far the layers' areas may sum from the answer's own: float addition only.
AREA_TOLERANCE_HA: Final[float] = 1e-6


# --------------------------------------------------------------------------- #
# The client
# --------------------------------------------------------------------------- #


class GisSettings(BaseSettings):
    """The sale system's own GIS_* block. The SDK reads no environment."""

    model_config = SettingsConfigDict(env_prefix="GIS_", env_file=".env", extra="ignore")

    #: The API's root; the client adds /api/v1.
    base_url: str
    api_key: SecretStr
    #: Seconds per request.
    timeout: float = 30.0
    #: A private CA's certificates. TLS is verified either way.
    ca_bundle: str | None = None


@functools.cache
def gis_settings() -> GisSettings:
    return GisSettings()


async def gis_client() -> AsyncIterator[gis_sdk.AgronextGisClient]:
    """A client, closed when the caller is done with it.

    One per request as written. Under load keep one for the process instead:
    open it in the app's lifespan, yield that one here, close it at shutdown —
    a client is safe to share between concurrent requests.
    """
    settings = gis_settings()
    async with gis_sdk.AgronextGisClient(
        base_url=settings.base_url,
        api_key=settings.api_key.get_secret_value(),
        timeout=settings.timeout,
        ca_bundle=settings.ca_bundle,
    ) as gis:
        yield gis


# --------------------------------------------------------------------------- #
# Triagem
# --------------------------------------------------------------------------- #


async def check_group(
    gis: gis_sdk.AgronextGisClient,
    /,
    plots: Sequence[Plot],
    *,
    municipality_id: int | None = None,
    min_share_pct: float | None = None,
) -> gis_sdk.GroupValidateResponse:
    """1. Whether the plots may be underwritten together, in their município.
    Writes nothing. One plot to twelve.

    `municipality_id` is the IBGE code the proposal declares: each plot needs a
    vertex in it and at least `min_share_pct` of its area inside it (None: the
    deployment's setting). Without it, the município the plots share is found.

    `valid` is the verdict and `errors` the reasons against: a plot farther than
    `thresholds.max_distance_km` from every other one, a plot with no vertex in
    the município, or a share below the bar. `warnings` never invalidate (a pair
    farther than `thresholds.ok_distance_km`). `pairs` has each pair's distance
    and status (none for one plot). `shared_municipality` is the município, with
    `per_polygon_pct`, each plot's share inside it. `thresholds` are the numbers
    judged with, the request's own bar included.

    Refused: an unknown IBGE code (`groups.validate.unknown_municipality`), and
    no plot or more than the ceiling (`groups.validate.polygon_count`), both 422.
    """
    return await gis.groups.validate(
        plots, municipality_id=municipality_id, min_shared_municipality_pct=min_share_pct
    )


async def list_car_properties(
    gis: gis_sdk.AgronextGisClient, /, plot: Plot
) -> gis_sdk.ScreeningPreflightResponse:
    """2. The CAR imóveis the plot touches. Writes nothing.

    Per candidate: the registration (`cod_imovel`, `status`/`status_label`,
    `condition`, `property_type`, `area_ha`, município, UF), how much OF THE PLOT
    it covers (`overlap_ha`, `overlap_pct`) and its boundary. `total` counts
    them all; `candidates` stops at 200. `car_snapshot` names the SICAR extract
    read. No candidates: the plot is on no registered imóvel.
    """
    return await gis.screening.preflight(plot)


async def screen_car_properties(
    gis: gis_sdk.AgronextGisClient, /, plot: Plot, cod_imoveis: Sequence[str]
) -> gis_sdk.ScreeningResponse:
    """3. ESG per CAR imóvel: every registry feature intersecting each one.

    The plot goes in as the área segurada, so each finding is reported twice:
    against the whole imóvel (`measured_against="imovel"`, what the norm reads)
    and against the insured field (`"area_segurada"`). Per imóvel: `outcome`
    (`not_in_snapshot` for a code the extract lacks — it never fails the
    batch), the registration as held, `findings` (`source`, `dataset`,
    `category`, `overlap_ha`/`overlap_pct` — None for a point feature —, the
    feature's attributes, `norm_reference` when CNSP 485/2025 names the layer)
    and `coverage`, the sources consulted for its UF.

    It reports and never decides: whether a finding blocks the sale is the
    caller's rule. Pins a run (`run_id`). At most 50 imóveis and 500 000 ha
    per call (`screening.screen.batch_too_large`, `.batch_area_too_large`).
    """
    return await gis.screening.screen(
        gis_sdk.ScreeningRequest(
            items=[
                gis_sdk.ScreeningItemRequest(cod_imovel=code, area_segurada=plot)
                for code in cod_imoveis
            ]
        )
    )


async def screen_plot(gis: gis_sdk.AgronextGisClient, /, plot: Plot) -> gis_sdk.OverlapsResponse:
    """4. ESG over the plot itself, no imóvel chosen. Writes nothing.

    `esg` lists every restriction feature crossing the plot, clipped to it,
    with `overlap_pct` as a share OF THE PLOT; `esg_covered_pct` is the plot's
    share under their union (areal features only). `car` is the CAR coverage:
    `covered_pct` of the plot under any imóvel, and the imóveis.
    """
    return await gis.screening.overlaps(plot)


async def check_policy_overlap(  # noqa: PLR0913 — the question's parameters, keyword-only
    gis: gis_sdk.AgronextGisClient,
    /,
    plot: Plot,
    *,
    product_id: int | None = None,
    season_ids: Sequence[int] | None = None,
    running_only: bool = True,
    planting_window_ids: Sequence[int] | None = None,
) -> gis_sdk.PolicyOverlapResponse:
    """5. Collisions with policies already sold. Writes nothing.

    `product_id` None asks every produto. `season_ids` None asks the safras
    OPEN TODAY; naming them asks exactly those. `running_only=False` includes
    policies stood down. `planting_window_ids` narrows to those windows — a
    policy loaded with no window is always included.

    Per match: `policy_id`, safra, produto, window, `overlap_ha` and
    `overlap_pct` (a share OF THE PLOT). `checked_seasons` is what an empty
    `matches` was asked of; `unchecked_undated_seasons` lists safras with no
    period, which are never open and so were not asked.
    """
    return await gis.policies.check_overlap(
        gis_sdk.PolicyOverlapRequest(
            geometry=plot,
            product_id=product_id,
            season_ids=season_ids,
            running_only=running_only,
            planting_window_ids=planting_window_ids,
        )
    )


@dataclass(frozen=True, slots=True)
class PlotTriagem:
    car: gis_sdk.ScreeningPreflightResponse
    #: None when the plot is on no imóvel.
    car_screening: gis_sdk.ScreeningResponse | None
    esg: gis_sdk.OverlapsResponse
    policies: gis_sdk.PolicyOverlapResponse


@dataclass(frozen=True, slots=True)
class Triagem:
    group: gis_sdk.GroupValidateResponse
    #: In the order the plots were given.
    plots: Sequence[PlotTriagem]


async def run_triagem(
    gis: gis_sdk.AgronextGisClient,
    /,
    plots: Sequence[Plot],
    *,
    municipality_id: int | None = None,
    min_share_pct: float | None = None,
    product_id: int | None = None,
) -> Triagem:
    """The whole Triagem, in order: the group in its município, then per plot
    its CAR imóveis, their screening, the plot's own ESG, and the policy
    collisions."""
    group = await check_group(
        gis, plots, municipality_id=municipality_id, min_share_pct=min_share_pct
    )
    screened: list[PlotTriagem] = []
    for plot in plots:
        car = await list_car_properties(gis, plot)
        codes = [candidate.cod_imovel for candidate in car.candidates]
        screened.append(
            PlotTriagem(
                car=car,
                car_screening=await screen_car_properties(gis, plot, codes) if codes else None,
                esg=await screen_plot(gis, plot),
                policies=await check_policy_overlap(gis, plot, product_id=product_id),
            )
        )
    return Triagem(group=group, plots=screened)


# --------------------------------------------------------------------------- #
# Resolver
# --------------------------------------------------------------------------- #


class GisLookupError(LookupError):
    """A produto, franquia or safra the GIS does not hold."""

    def __init__(self, product_code: str, missing: str) -> None:
        super().__init__(f"{product_code}: {missing} is not in the GIS")


@dataclass(frozen=True, slots=True)
class RateCell:
    """What a rate is asked of: one safra, one produto, one franquia."""

    season: gis_sdk.SeasonItem
    product: gis_sdk.ProductItem
    deductible: gis_sdk.DeductibleItem


async def find_rate_cell(
    gis: gis_sdk.AgronextGisClient,
    /,
    *,
    product_code: str,
    deductible: Decimal,
    season_label: str | None = None,
) -> RateCell:
    """The ids behind a produto code, a franquia (0.20 for 20%) and a safra label.

    No label: the newest safra that sells the produto. Ask once and keep it —
    these change only when someone edits the catalogue.
    """
    products = await gis.products.list_products()
    product = next((item for item in products if item.code == product_code), None)
    if product is None:
        raise GisLookupError(product_code, "the produto")
    seasons = await gis.products.list_product_seasons(product.id)
    season = next(
        (item for item in seasons if season_label is None or item.label == season_label), None
    )
    if season is None:
        raise GisLookupError(product_code, f"safra {season_label or 'selling it'}")
    franquias = await gis.products.list_deductibles(product.id)
    franquia = next((item for item in franquias if item.value == deductible), None)
    if franquia is None:
        raise GisLookupError(product_code, f"franquia {deductible}")
    return RateCell(season=season, product=product, deductible=franquia)


async def sold_territory(
    gis: gis_sdk.AgronextGisClient, /, cell: RateCell
) -> list[gis_sdk.SoldTerritoryItem]:
    """1. "À venda": the UFs, and their municípios, where this franquia has a price.

    The API answers for the (safra, produto): a município is listed when a rate
    reaches it inside the liberada, with the franquias on offer there
    (`deductible_ids`). Narrowed here to the one franquia, as the UI does.
    """
    territory = await gis.pairs.territory(cell.season.id, cell.product.id)
    narrowed = [
        state.model_copy(
            update={
                "municipalities": [
                    municipality
                    for municipality in state.municipalities
                    if cell.deductible.id in municipality.deductible_ids
                ]
            }
        )
        for state in territory
    ]
    return [state for state in narrowed if state.municipalities]


async def resolve_plot(
    gis: gis_sdk.AgronextGisClient, /, plot: Plot, cell: RateCell
) -> gis_sdk.RateResolutionResponse:
    """2. The rate over one plot, at the grid resolution the API recommends.

    `aggregate_value` (comercial) and `aggregate_risk_value` (risco) are
    area-weighted over the plot's tiles, in the unit the rates were written in
    (13.19 is 13.19%); `aggregate_expected_yield_kg_ha` is None unless every
    tile states one. `area_ha` is the plot as the tiles measure it. Pins a run
    (`run_id`).

    `layers` holds every parameter of that number. Each entry is one área (and
    one bonificação/agravamento, if any) that won tiles: `value`/`risk_value`
    are what it charged, `area_ha` its weight, `level` and `name` which área it
    is. In `ratio` mode `reference_value`/`reference_risk_value` are the
    reference layer's rates and `commercial_ratio`/`risk_ratio` (on the answer)
    the fator. `adjustment` is the bonificação (negative `percent`) or
    agravamento of the CAR imóvel those tiles lie in, with the rate before it.
    It moves the commercial rate only. `verify_resolution` redoes the
    arithmetic.

    The whole plot is priced or nothing is: a plot touching the proibida is
    refused (`FORBIDDEN_AREA`), one with ground no rate reaches too
    (`UNPRICED_AREA`), both as `gis_sdk.UnprocessableError`.
    """
    options = await gis.rates.preflight(plot)
    return await gis.rates.resolve(
        plot,
        season_id=cell.season.id,
        product_id=cell.product.id,
        deductible_id=cell.deductible.id,
        cell_m=options.recommended_cell_m,
    )


def _rounded(value: Decimal, factor: Decimal) -> Decimal:
    """One step of a rate: times a factor, half-even to the API's quantum."""
    return (value * factor).quantize(RATE_QUANTUM, rounding=ROUND_HALF_EVEN)


def verify_resolution(answer: gis_sdk.RateResolutionResponse) -> list[str]:
    """Redo a resolution's arithmetic from the answer alone; empty when it holds.

    Per layer: in `ratio` mode, reference rate * fator, then * (1 + percent/100)
    under the adjustment, each step half-even. Then each aggregate: the layers'
    rates weighted by their `area_ha`, half-up.
    """
    problems: list[str] = []
    for layer in answer.layers:
        before = layer.value if layer.adjustment is None else layer.adjustment.unadjusted_value
        if answer.mode is gis_sdk.RateMode.RATIO:
            if (
                layer.reference_value is None
                or layer.reference_risk_value is None
                or answer.commercial_ratio is None
                or answer.risk_ratio is None
            ):
                problems.append(f"layer {layer.index}: ratio mode without its fator's inputs")
                continue
            if _rounded(layer.reference_value, answer.commercial_ratio) != before:
                problems.append(f"layer {layer.index}: comercial is not reference * fator")
            if _rounded(layer.reference_risk_value, answer.risk_ratio) != layer.risk_value:
                problems.append(f"layer {layer.index}: risco is not reference * fator")
        if layer.adjustment is not None:
            factor = 1 + layer.adjustment.percent / 100
            if _rounded(before, factor) != layer.value:
                problems.append(f"layer {layer.index}: the adjustment does not give the value")

    weights = [Decimal(layer.area_ha) for layer in answer.layers]
    total = sum(weights, Decimal(0))
    if abs(float(total) - answer.area_ha) > AREA_TOLERANCE_HA:
        problems.append(f"layers cover {total} ha of {answer.area_ha}")
    for label, values, stated in (
        ("comercial", [layer.value for layer in answer.layers], answer.aggregate_value),
        ("risco", [layer.risk_value for layer in answer.layers], answer.aggregate_risk_value),
    ):
        weighted = sum((w * v for w, v in zip(weights, values, strict=True)), Decimal(0))
        recomputed = (weighted / total).quantize(RATE_QUANTUM, rounding=ROUND_HALF_UP)
        if recomputed != stated:
            problems.append(f"{label}: {recomputed} recomputed, {stated} answered")
    return problems


@dataclass(frozen=True, slots=True)
class PolicyRate:
    plots: Sequence[gis_sdk.RateResolutionResponse]
    total_area_ha: float
    #: Area-weighted over the plots, as the API weights tiles inside one.
    #: None only if a plot's answer carried none.
    commercial: Decimal | None
    risk: Decimal | None


async def resolve_plots(
    gis: gis_sdk.AgronextGisClient, /, plots: Sequence[Plot], cell: RateCell
) -> PolicyRate:
    """The rate per plot, and over all of them, weighted by each answer's `area_ha`."""
    answers = [await resolve_plot(gis, plot, cell) for plot in plots]
    weights = [Decimal(answer.area_ha) for answer in answers]
    total = sum(weights, Decimal(0))

    def weighted(values: Sequence[Decimal | None]) -> Decimal | None:
        present = [value for value in values if value is not None]
        if len(present) < len(values):
            return None
        return sum((w * v for w, v in zip(weights, present, strict=True)), Decimal(0)) / total

    return PolicyRate(
        plots=answers,
        total_area_ha=float(total),
        commercial=weighted([answer.aggregate_value for answer in answers]),
        risk=weighted([answer.aggregate_risk_value for answer in answers]),
    )


# --------------------------------------------------------------------------- #
# A run, end to end
# --------------------------------------------------------------------------- #


def square(lon: float, lat: float, side_deg: float = 0.004) -> Plot:
    """A small square field around a point: enough for the demo."""
    west, south, east, north = lon, lat, lon + side_deg, lat + side_deg
    ring = [[west, south], [east, south], [east, north], [west, north], [west, south]]
    return {"type": "Polygon", "coordinates": [ring]}


async def main() -> None:
    # Two fields about a kilometre apart in Fraiburgo (SC), inside PERA's liberada.
    plots = [square(-50.8766, -27.0313), square(-50.8666, -27.0313)]

    async with contextlib.asynccontextmanager(gis_client)() as gis:
        # The proposal declares Fraiburgo (IBGE 4205506); each field must lie
        # at least 80% inside it.
        triagem = await run_triagem(gis, plots, municipality_id=4205506, min_share_pct=80)
        shared = triagem.group.shared_municipality
        logger.info(
            "group valid=%s in %s %s (bar %s%%) errors=%s warnings=%s",
            triagem.group.valid,
            shared.name if shared else None,
            list(shared.per_polygon_pct) if shared else None,
            triagem.group.thresholds.min_shared_municipality_pct,
            triagem.group.errors,
            triagem.group.warnings,
        )
        for index, screened in enumerate(triagem.plots, start=1):
            logger.info(
                "plot %d: %d CAR imóvel(is), ESG %.1f%% covered by %d feature(s), "
                "%d policy collision(s)",
                index,
                screened.car.total,
                screened.esg.esg_covered_pct,
                len(screened.esg.esg),
                screened.policies.total_matches,
            )
            for result in screened.car_screening.results if screened.car_screening else ():
                for finding in result.findings:
                    logger.info(
                        "  %s %s/%s %s%%",
                        result.cod_imovel,
                        finding.source,
                        finding.category,
                        finding.overlap_pct,
                    )

        cell = await find_rate_cell(gis, product_code="PERA", deductible=Decimal("0.20"))
        for state in await sold_territory(gis, cell):
            logger.info("à venda: %s, %d município(s)", state.abbr, len(state.municipalities))
        try:
            rate = await resolve_plots(gis, plots, cell)
        except gis_sdk.UnprocessableError as refused:
            if refused.code not in (FORBIDDEN_AREA, UNPRICED_AREA):
                raise
            logger.info("not sold there: %s (%s)", refused.code, refused.detail)
            return
        for index, answer in enumerate(rate.plots, start=1):
            logger.info(
                "plot %d: %.2f ha, comercial %s, risco %s (run %d, %s mode, fator %s)",
                index,
                answer.area_ha,
                answer.aggregate_value,
                answer.aggregate_risk_value,
                answer.run_id,
                answer.mode,
                answer.commercial_ratio,
            )
            for layer in answer.layers:
                logger.info(
                    "  %s %s: %s -> %s over %.2f ha%s",
                    layer.level,
                    layer.name,
                    layer.reference_value,
                    layer.value,
                    layer.area_ha,
                    ""
                    if layer.adjustment is None
                    else f" ({layer.adjustment.percent:+}% on CAR {layer.adjustment.name})",
                )
            logger.info("  verified: %s", verify_resolution(answer) or "ok")
        logger.info(
            "policy: %.2f ha, comercial %s, risco %s",
            rate.total_area_ha,
            rate.commercial,
            rate.risk,
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    asyncio.run(main())
