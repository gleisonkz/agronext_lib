"""Validate agronext_gis_sdk against a LIVE agronext_gis API: one sale, walked call by call.

    cd agronext_gis_sdk
    uv run --env-file ../.env python example.py                 # the safra open today
    uv run --env-file ../.env python example.py --season-id 8   # one safra, by its id

`GIS_BASE_URL` is the API it talks to and `GIS_API_KEY` the key of a calling
system registered there (in the UI: Usuários) — the `GIS_*` block of the
project's `.env.example`. Every request goes over the network to that API, as a
sale system's does. Nothing stands in for it, here or in how this is run.

The nine calls of `gis.underwriting`, in the order a sale makes them. The first
takes nothing; every other is fed by the answers before it, so no id is ever
known in advance — a safra's included.

Before the purchase — the buyer knows the crop, the peril and where they plant,
not the product:

1. `list_open_seasons`      the safras being sold today, each with its id
2. `list_sold_territory`    where anything is on sale in the safra picked
3. `list_products_on_sale`  what is on sale in the buyer's município
4. `list_car_properties`    per polygon drawn: the CAR imóveis under it, to pick one
5. `validate_group`         more than one polygon: may they go in one contract
6. `resolve_rates`          what it costs, for the produto and franquia picked

After it — the contract goes to underwriting, which screens it:

7. `screen_car_properties`  the registries on the CAR imóveis picked
8. `screen_polygons`        the registries over the polygons themselves
9. `check_policy_overlap`   collisions with policies already sold

ALL NINE ARE MADE, OR THE RUN ENDS NON-ZERO. Exit 2: it could not reach the
next call, and says why — no safra open, a safra with nothing on sale, fields no
rate reaches. Exit 1: a request failed — the API refused or failed it, or
answered something the SDK cannot read — and the line names the request. So a
run ending `9 calls answered` is the SDK and that API agreeing on every request
and every answer of a sale.

What a buyer would pick on screen, an option names by the id the run itself
printed: the safra (call 1 lists them), the município (its IBGE code), the
produto and the franquia (call 3 lists them). Unnamed, the safra is the one open
today and each of the others the first offered. The fields are two squares about
the município's centre, and the CAR imóvel picked under each is the one covering
most of it.

One function per call. Each takes the client first and builds nothing, so one
place owns the client: `gis_client`, an async generator, which is what a FastAPI
`Depends` takes as it stands. Those ten are the part to copy into a sale system.
A failure is a `gis_sdk.AgronextGisError`; a refusal is an `ApiError` subclass
whose `code` is what to branch on, never the wording.
"""

import asyncio
import contextlib
import functools
import logging
from collections.abc import AsyncGenerator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Final

import typer
from pydantic import BeforeValidator, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

import agronext_gis_sdk as gis_sdk

logger = logging.getLogger("agronext_gis_sdk.example")

#: One field of a sale, as the buyer drew it: a GeoJSON Polygon or MultiPolygon
#: in EPSG:4326, `[longitude, latitude]`, or anything with `__geo_interface__`.
type Polygon = gis_sdk.GeometryInput

#: A request failed: the API refused or failed it, never answered, or answered
#: something the SDK cannot read. What a validation run exists to find.
EXIT_FAILED: Final[int] = 1

#: The run could not reach its next call, or a setting is missing: a refusal
#: that says what to change, not a crash.
EXIT_STOPPED: Final[int] = 2

#: How many calls a sale makes — what a whole run reports having had answered.
CALLS: Final[int] = 9


# --------------------------------------------------------------------------- #
# The client
# --------------------------------------------------------------------------- #


def _blank_is_unset(value: object) -> object:
    """`GIS_CA_BUNDLE=` in an env file means UNSET, not a bundle at the empty path."""
    if isinstance(value, str) and not value.strip():
        return None
    return value


class GisSettings(BaseSettings):
    """The caller's own GIS_* block. The SDK reads no environment."""

    model_config = SettingsConfigDict(env_prefix="GIS_", env_file=".env", extra="ignore")

    #: The API's root; the client adds /api/v1.
    base_url: str
    api_key: SecretStr
    #: Seconds per request.
    timeout: float = 30.0
    #: A private CA's certificates. TLS is verified either way.
    ca_bundle: Annotated[Path | None, BeforeValidator(_blank_is_unset)] = None


@functools.cache
def gis_settings() -> GisSettings:
    return GisSettings()


async def gis_client() -> AsyncGenerator[gis_sdk.AgronextGisClient, None]:
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
# Before the purchase
# --------------------------------------------------------------------------- #


async def list_open_seasons(gis: gis_sdk.AgronextGisClient, /) -> list[gis_sdk.SeasonItem]:
    """1. The safras being sold today, each with its id — what the safra of the
    sale is picked from. Usually one; two while the next is already selling."""
    return await gis.underwriting.list_open_seasons()


async def list_sold_territory(
    gis: gis_sdk.AgronextGisClient, /, season_id: int
) -> gis_sdk.SeasonTerritoryResponse:
    """2. The states with something on sale this safra, and under each the
    municípios that have it — what the buyer picks their município from."""
    return await gis.underwriting.list_sold_territory(season_id)


async def list_products_on_sale(
    gis: gis_sdk.AgronextGisClient, /, season_id: int, municipality_id: int
) -> gis_sdk.ProductsOnSaleResponse:
    """3. The produtos on sale in that município, each with its crop, its peril
    and the franquias on offer there — what the buyer picks a produto from."""
    return await gis.underwriting.list_products_on_sale(season_id, municipality_id)


async def list_car_properties(
    gis: gis_sdk.AgronextGisClient, /, polygon: Polygon
) -> gis_sdk.ScreeningPreflightResponse:
    """4. The CAR imóveis one drawn polygon touches, largest overlap first —
    what the buyer picks the polygon's imóvel from. Asked per polygon, as drawn."""
    return await gis.underwriting.list_car_properties(polygon)


async def validate_group(
    gis: gis_sdk.AgronextGisClient,
    /,
    polygons: Sequence[Polygon],
    *,
    municipality_id: int,
    min_shared_municipality_pct: float | None = None,
) -> gis_sdk.GroupValidateResponse:
    """5. Whether the polygons may go in one contract, in the município the
    sale is in. `valid` False is an answer, with the reasons in `errors`."""
    return await gis.underwriting.validate_group(
        polygons,
        municipality_id=municipality_id,
        min_shared_municipality_pct=min_shared_municipality_pct,
    )


async def resolve_rates(
    gis: gis_sdk.AgronextGisClient,
    /,
    polygons: Sequence[Polygon],
    *,
    season_id: int,
    product_id: int,
    deductible_id: int,
) -> gis_sdk.RateResolutionPolygonsResponse:
    """6. The rate of the sale and of each polygon, for the produto and the
    franquia picked. Raises `gis_sdk.PolygonsRefusedError` when a polygon cannot
    be resolved: nothing was, and its `refusals` say which and why."""
    return await gis.underwriting.resolve_rates(
        polygons, season_id=season_id, product_id=product_id, deductible_id=deductible_id
    )


# --------------------------------------------------------------------------- #
# After it: underwriting screens the contract
# --------------------------------------------------------------------------- #


async def screen_car_properties(
    gis: gis_sdk.AgronextGisClient, /, car_codes: Sequence[str]
) -> gis_sdk.ScreeningResponse:
    """7. What the registries hold on the CAR imóveis picked in step 4, by
    their codes. `run_id` pins the answer."""
    return await gis.underwriting.screen_car_properties(car_codes)


async def screen_polygons(
    gis: gis_sdk.AgronextGisClient, /, polygons: Sequence[Polygon]
) -> gis_sdk.OverlapsPolygonsResponse:
    """8. What the registries hold over each polygon itself."""
    return await gis.underwriting.screen_polygons(polygons)


async def check_policy_overlap(  # noqa: PLR0913 — the question's own parameters, keyword-only
    gis: gis_sdk.AgronextGisClient,
    /,
    polygons: Sequence[Polygon],
    *,
    product_id: int | None = None,
    season_ids: Sequence[int] | None = None,
    running_only: bool = True,
    planting_window_ids: Sequence[int] | None = None,
) -> gis_sdk.PolicyOverlapPolygonsResponse:
    """9. Whether any polygon collides with a policy already sold. Unnarrowed,
    it asks the running policies of every produto in the safras open today."""
    return await gis.underwriting.check_policy_overlap(
        polygons,
        product_id=product_id,
        season_ids=season_ids,
        running_only=running_only,
        planting_window_ids=planting_window_ids,
    )


# --------------------------------------------------------------------------- #
# One sale, end to end, against the live API
# --------------------------------------------------------------------------- #

#: The fields the run sells: squares this many degrees a side (about 19 ha this
#: far south), their centres this far apart.
FIELD_SIDE_DEG: Final[float] = 0.004
FIELD_GAP_DEG: Final[float] = 0.01


class SaleStoppedError(Exception):
    """The run cannot reach its next call. The message says what kept it, and
    what to name instead."""


@dataclass(frozen=True, slots=True)
class Picks:
    """What a buyer would pick on screen, where the run names it. None: the
    safra open today, and the first offered of the rest."""

    season_id: int | None = None
    municipality_id: int | None = None
    product_id: int | None = None
    deductible_id: int | None = None


@dataclass(frozen=True, slots=True)
class Offer:
    """What the buyer picked from what is on sale: calls 1 to 3, answered."""

    season_id: int
    municipality_id: int
    product: gis_sdk.OnSaleProductItem
    deductible: gis_sdk.DeductibleItem


@dataclass(frozen=True, slots=True)
class Fields:
    """What the buyer drew, and the CAR imóvel picked under each: call 4, answered."""

    polygons: Sequence[Polygon]
    car_codes: Sequence[str]


def report(call: str, *answers: str) -> None:
    """The result of one call, on stdout: its name, and a line per thing it answered."""
    for position, answer in enumerate(answers):
        typer.echo(f"{call if position == 0 else '':<23}{answer}")


def square(lon: float, lat: float) -> gis_sdk.GeoJson:
    """A square field centred on a point."""
    half = FIELD_SIDE_DEG / 2
    west, south, east, north = lon - half, lat - half, lon + half, lat + half
    ring = [[west, south], [east, south], [east, north], [west, north], [west, south]]
    return {"type": "Polygon", "coordinates": [ring]}


def picked_season(open_today: Sequence[gis_sdk.SeasonItem], season_id: int | None) -> int:
    """The safra being sold: the one named, or the one open today."""
    if season_id is not None:
        return season_id
    if len(open_today) != 1:
        msg = (
            "no safra is open today, so nothing is being sold"
            if not open_today
            else f"{len(open_today)} safras are open today: name the one being sold "
            "with --season-id"
        )
        raise SaleStoppedError(msg)
    return open_today[0].id


def picked_product(
    on_sale: gis_sdk.ProductsOnSaleResponse, product_id: int | None
) -> gis_sdk.OnSaleProductItem:
    """The produto the buyer picks from what is on sale there: the one named,
    or the first offered."""
    offered = [item for item in on_sale.products if product_id is None or item.id == product_id]
    if not offered:
        place = f"município {on_sale.municipality_id} in safra {on_sale.season_id}"
        msg = (
            f"nothing is on sale in {place}: name another with --municipality-id"
            if product_id is None
            else f"produto {product_id} is not on sale in {place}: name one that is "
            "with --product-id"
        )
        raise SaleStoppedError(msg)
    return offered[0]


def picked_deductible(
    product: gis_sdk.OnSaleProductItem, deductible_id: int | None
) -> gis_sdk.DeductibleItem:
    """The franquia the buyer picks from the ones on offer: the one named, or
    the first offered."""
    offered = [
        item for item in product.deductibles if deductible_id is None or item.id == deductible_id
    ]
    if not offered:
        msg = (
            f"franquia {deductible_id} is not on offer for produto {product.code} there: "
            "name one of its own with --deductible-id, or its produto with --product-id"
        )
        raise SaleStoppedError(msg)
    return offered[0]


async def pick_offer(gis: gis_sdk.AgronextGisClient, /, picks: Picks) -> Offer:
    """Calls 1, 2 and 3: the safras open today, where anything is on sale in
    the one picked, and what is sold where the buyer plants.

    Each answer is reported BEFORE anything is picked from it, with the id of
    every thing that can be picked — so an option never needs an id the run did
    not print.
    """
    open_today = await list_open_seasons(gis)
    report(
        "list_open_seasons",
        *(
            f"safra {season.id}: {season.label}, {season.starts_on} to {season.ends_on}"
            for season in open_today
        ),
        *([] if open_today else ["no safra is open today"]),
    )
    season_id = picked_season(open_today, picks.season_id)
    if season_id not in {season.id for season in open_today}:
        # Said, not refused: the API answers for any safra. But it is in no
        # listing a sale starts from, so this run is not a sale as one is made.
        logger.warning("safra %d is not open today: a sale would not be made in it", season_id)

    territory = await list_sold_territory(gis, season_id)
    if not territory.states:
        msg = f"nothing is on sale in safra {season_id}"
        raise SaleStoppedError(msg)
    report(
        "list_sold_territory",
        *(
            f"safra {season_id}, {state.abbr}: {len(state.municipalities)} município(s), "
            f"the first {state.municipalities[0].municipality_id} {state.municipalities[0].name}"
            for state in territory.states
        ),
    )
    municipality_id = (
        picks.municipality_id
        if picks.municipality_id is not None
        else territory.states[0].municipalities[0].municipality_id
    )

    on_sale = await list_products_on_sale(gis, season_id, municipality_id)
    report(
        "list_products_on_sale",
        *(
            f"município {municipality_id}, produto {offered.id}: {offered.code} "
            f"({offered.crop}, {offered.peril}); franquias "
            + ", ".join(f"{franquia.id}: {franquia.value}" for franquia in offered.deductibles)
            for offered in on_sale.products
        ),
        *([] if on_sale.products else [f"município {municipality_id}: nothing on sale"]),
    )
    product = picked_product(on_sale, picks.product_id)
    deductible = picked_deductible(product, picks.deductible_id)
    report(
        "",
        f"picked: produto {product.id} ({product.code}), "
        f"franquia {deductible.id} ({deductible.value})",
    )
    return Offer(
        season_id=season_id,
        municipality_id=municipality_id,
        product=product,
        deductible=deductible,
    )


async def draw_fields(gis: gis_sdk.AgronextGisClient, /, municipality_id: int) -> Fields:
    """The buyer draws, and call 4 under each field: the CAR imóveis it touches."""
    place = await gis.geography.get_municipality(municipality_id)
    lon, lat = place.centroid
    polygons = [square(lon, lat), square(lon + FIELD_GAP_DEG, lat)]

    car_codes: list[str] = []
    answers: list[str] = []
    for index, polygon in enumerate(polygons):
        found = await list_car_properties(gis, polygon)
        if found.candidates:
            car_codes.append(found.candidates[0].cod_imovel)
        picked = f"picked {car_codes[-1]}" if found.candidates else "none to pick"
        answers.append(
            f"polygon {index} in {place.name}/{place.state_abbr}: "
            f"{found.total} CAR imóvel(is), {picked}"
        )
    report("list_car_properties", *answers)
    if not car_codes:
        msg = (
            f"no CAR imóvel lies under the fields drawn in município {municipality_id}, "
            "so there is none to screen: name another place with --municipality-id"
        )
        raise SaleStoppedError(msg)
    return Fields(polygons=polygons, car_codes=car_codes)


async def price(gis: gis_sdk.AgronextGisClient, /, offer: Offer, fields: Fields) -> None:
    """Calls 5 and 6: the group, and what the sale costs."""
    group = await validate_group(gis, fields.polygons, municipality_id=offer.municipality_id)
    report("validate_group", f"valid={group.valid}", *group.errors, *group.warnings)

    try:
        rate = await resolve_rates(
            gis,
            fields.polygons,
            season_id=offer.season_id,
            product_id=offer.product.id,
            deductible_id=offer.deductible.id,
        )
    except gis_sdk.PolygonsRefusedError as refused:
        reasons = "; ".join(
            f"polygon {refusal.polygon_index}: {refusal.code} ({refusal.detail})"
            for refusal in refused.refusals
        )
        msg = f"the fields cannot be sold — {reasons}: name another place with --municipality-id"
        raise SaleStoppedError(msg) from refused
    report(
        "resolve_rates",
        f"the sale, {rate.area_ha:.2f} ha: comercial {rate.aggregate_value}, "
        f"risco {rate.aggregate_risk_value}",
        *(
            f"polygon {item.polygon_index}, {item.area_ha:.2f} ha: "
            f"comercial {item.aggregate_value}, risco {item.aggregate_risk_value} "
            f"(run {item.run_id}, {item.cell_m} m grid)"
            for item in rate.polygons
        ),
    )


async def underwrite(gis: gis_sdk.AgronextGisClient, /, offer: Offer, fields: Fields) -> None:
    """Calls 7, 8 and 9: the contract, screened."""
    screening = await screen_car_properties(gis, fields.car_codes)
    report(
        "screen_car_properties",
        *(
            f"{result.cod_imovel}: {result.outcome}, {len(result.findings)} finding(s)"
            for result in screening.results
        ),
        f"pinned as run {screening.run_id}",
    )

    registries = await screen_polygons(gis, fields.polygons)
    report(
        "screen_polygons",
        *(
            f"polygon {screened.polygon_index}: {len(screened.esg)} registry feature(s) "
            f"over {screened.esg_covered_pct:.1f}% of it"
            for screened in registries.polygons
        ),
    )

    overlap = await check_policy_overlap(
        gis, fields.polygons, product_id=offer.product.id, season_ids=[offer.season_id]
    )
    report(
        "check_policy_overlap",
        f"{overlap.total_matches} collision(s) with policies of {offer.product.code} "
        f"in {', '.join(checked.label for checked in overlap.checked_seasons)}",
    )


async def walk(picks: Picks) -> None:
    """One sale, all nine calls, each fed by the answers before it."""
    async with contextlib.asynccontextmanager(gis_client)() as gis:
        offer = await pick_offer(gis, picks)
        fields = await draw_fields(gis, offer.municipality_id)
        await price(gis, offer, fields)
        # The buyer accepts and the purchase is concluded: the sale system's own
        # step. The contract then goes to underwriting.
        await underwrite(gis, offer, fields)


def failure(failed: gis_sdk.AgronextGisError) -> str:
    """What went wrong with a request, as the run reports it."""
    if isinstance(failed, gis_sdk.ApiError):
        return f"{failed.method} {failed.url}: {failed} (correlation id {failed.correlation_id})"
    if isinstance(failed, gis_sdk.ResponseMismatchError):
        # The cause is what the answer did not fit: which field, and why.
        return f"{failed}\n{failed.__cause__}"
    return str(failed)


def checked_settings() -> GisSettings:
    """The `GIS_*` block, or a refusal that names the key to set — a person's
    environment, not a pydantic traceback."""
    try:
        return gis_settings()
    except ValidationError as invalid:
        for error in invalid.errors():
            logger.error("GIS_%s: %s", str(error["loc"][0]).upper(), error["msg"])  # noqa: TRY400
        logger.error("set them in the environment: see GIS_* in .env.example")  # noqa: TRY400
        raise typer.Exit(EXIT_STOPPED) from invalid


app = typer.Typer(
    add_completion=False,
    # A traceback must never print what its frames hold: one of them holds the key.
    pretty_exceptions_show_locals=False,
    help="Validate agronext_gis_sdk against a live agronext_gis API: one sale, nine calls.",
)


@app.command()
def sale(
    season_id: Annotated[
        int | None,
        typer.Option(
            "--season-id",
            metavar="ID",
            help="The safra being sold, by the id the run prints first. "
            "Unnamed: the one open today.",
        ),
    ] = None,
    municipality_id: Annotated[
        int | None,
        typer.Option(
            "--municipality-id",
            metavar="IBGE",
            help="Where the buyer plants, by IBGE code. Unnamed: the first município on sale.",
        ),
    ] = None,
    product_id: Annotated[
        int | None,
        typer.Option(
            "--product-id",
            metavar="ID",
            help="The produto the buyer picks, by the id of one on sale there. Unnamed: the first.",
        ),
    ] = None,
    deductible_id: Annotated[
        int | None,
        typer.Option(
            "--deductible-id",
            metavar="ID",
            help="The franquia the buyer picks, by the id of one on offer there. "
            "Unnamed: the produto's first.",
        ),
    ] = None,
) -> None:
    """Walk one sale against the API GIS_BASE_URL names: every call answered, or
    a non-zero stop saying what kept the run from the next one."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")
    logger.info("validating against %s", checked_settings().base_url)
    try:
        asyncio.run(
            walk(
                Picks(
                    season_id=season_id,
                    municipality_id=municipality_id,
                    product_id=product_id,
                    deductible_id=deductible_id,
                )
            )
        )
    except SaleStoppedError as stopped:
        logger.error("%s", stopped)  # noqa: TRY400 — one line, not a traceback
        raise typer.Exit(EXIT_STOPPED) from stopped
    except gis_sdk.AgronextGisError as failed:
        logger.error("%s", failure(failed))  # noqa: TRY400 — logged ONCE, here, by what it is
        raise typer.Exit(EXIT_FAILED) from failed
    typer.echo(f"{CALLS} calls answered")


if __name__ == "__main__":
    app()
