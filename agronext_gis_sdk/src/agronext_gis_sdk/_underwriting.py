"""`gis.underwriting` — the calls a sale system makes, in the order it makes them.

The other namespaces follow the API, one method per route, for whoever manages
the catalogue through it: safras, produtos, rates, abrangências. This one
follows a SALE. Each call takes what the caller holds at that step and returns
what the next step needs, so nothing is ever looked up or scanned on the way:

1. `list_open_seasons()` — the safras being sold today. It takes nothing: it
   is where a sale starts, and where the `season_id` of every call below comes
   from.
2. `list_sold_territory(season_id)` — the buyer knows where they plant, not
   what is sold. This answers WHERE: the states and municípios with something
   on sale this safra, and nothing else, so nobody is offered an empty place.
3. `list_products_on_sale(season_id, municipality_id)` — for the município the
   buyer picked: each produto with its crop, its peril and the franquias on
   offer there. The ids it returns are what pricing a polygon takes.
4. `list_car_properties(polygon)` — as each polygon is drawn: the CAR imóveis it
   touches, for the buyer to pick the one the polygon belongs to.
5. `validate_group(polygons, municipality_id=…)` — once there is more than one
   polygon: whether they may be underwritten together, in that município.
6. `resolve_rates(polygons, season_id=…, product_id=…, deductible_id=…)` — what
   the sale costs: every polygon's rate and the sale's, in one request.

The purchase is the caller's. After it, the contract is screened:

7. `screen_car_properties(car_codes)` — what the registries hold on the CAR
   imóveis picked in step 4.
8. `screen_polygons(polygons)` — what the registries hold over the polygons
   themselves.
9. `check_policy_overlap(polygons, …)` — whether any polygon collides with a
   policy already running.

From the group check on, every call takes ALL the polygons of the sale and is
one request: the API does the work per polygon and answers per polygon, in the
order given — no loop, and no arithmetic, on the caller's side. Whether a
finding blocks a sale is the caller's judgement: these calls report.

Nothing here speaks HTTP. Every method calls the route-level method that owns
the request, so there is one place per route that knows its path.
"""

from collections.abc import Sequence

from agronext_gis_sdk._groups import Groups, GroupValidateResponse
from agronext_gis_sdk._policies import (
    Policies,
    PolicyOverlapPolygonsRequest,
    PolicyOverlapPolygonsResponse,
)
from agronext_gis_sdk._rates import Rates, Seasons
from agronext_gis_sdk._rates_models import (
    ProductsOnSaleResponse,
    RateResolutionPolygonsResponse,
    SeasonItem,
    SeasonTerritoryResponse,
)
from agronext_gis_sdk._screening import (
    OverlapsPolygonsResponse,
    Screening,
    ScreeningItemRequest,
    ScreeningPreflightResponse,
    ScreeningRequest,
    ScreeningResponse,
)
from agronext_gis_sdk._wire import GeometryInput, to_geojson


class Underwriting:
    """`gis.underwriting` — a sale, step by step."""

    def __init__(
        self,
        *,
        seasons: Seasons,
        screening: Screening,
        groups: Groups,
        rates: Rates,
        policies: Policies,
    ) -> None:
        self._seasons = seasons
        self._screening = screening
        self._groups = groups
        self._rates = rates
        self._policies = policies

    async def list_open_seasons(self) -> list[SeasonItem]:
        """The safras being sold today: where a sale starts.

        A safra is open while today falls inside its period (`starts_on` to
        `ends_on`), and a safra nobody has dated is never open. Each carries its
        `id` — the `season_id` every call below takes — and its `label`, which
        is what a buyer reads. Newest period first.

        More than one can be open at once: the next safra starts selling while
        the current one still runs, and the buyer then picks which. None open:
        nothing is being sold today.
        """
        return await self._seasons.list_open_seasons()

    async def list_sold_territory(self, season_id: int) -> SeasonTerritoryResponse:
        """Where anything is on sale in the safra: only the states that have
        produtos and, under each, only the municípios with rates.

        `season_id` is the safra being sold, from `list_open_seasons`. Each
        município carries its IBGE code (`municipality_id`), which is what
        `list_products_on_sale` and the group check take.

        The API holds this listing and refreshes it when rates, fatores or an
        abrangência change; `refreshed_at` is when it last did. A place listed
        here is never a promise of a price: the rate is always resolved from
        the rates themselves.
        """
        return await self._seasons.list_sold_territory(season_id)

    async def list_products_on_sale(
        self, season_id: int, municipality_id: int
    ) -> ProductsOnSaleResponse:
        """What is on sale in one município this safra.

        Each produto carries `code`, `name`, `crop` and `peril` — what a buyer
        is narrowed by — and `deductibles`, the franquias on offer THERE, each
        with its `id` and `value` (0.20 is 20%), ascending. A produto's `id` and
        a franquia's `id` are what resolving a rate takes.

        No products: nothing is sold there. An IBGE code that does not exist
        raises `NotFoundError`, and so does a safra that does not.
        """
        return await self._seasons.list_products_on_sale(season_id, municipality_id)

    async def list_car_properties(self, polygon: GeometryInput) -> ScreeningPreflightResponse:
        """The CAR imóveis one drawn polygon touches, largest overlap first.

        Asked as each polygon is drawn, so the buyer picks the imóvel it
        belongs to: the API never picks one, and a caller must not either.
        Each candidate carries its CAR code (`cod_imovel` — what
        `screen_car_properties` takes), its SICAR status and condition, its
        declared area, its município, how much OF THE POLYGON it covers
        (`overlap_ha`, `overlap_pct`) and its outline.

        `total` is how many the polygon touches; `candidates` holds at most
        200 of them. `car_snapshot` is the copy of SICAR that was read. A
        polygon that cannot be read raises `UnprocessableError`
        (`geometry.invalid`).
        """
        return await self._screening.preflight(polygon)

    async def validate_group(
        self,
        polygons: Sequence[GeometryInput],
        *,
        municipality_id: int,
        min_shared_municipality_pct: float | None = None,
    ) -> GroupValidateResponse:
        """Whether the polygons of one sale may be underwritten together.

        `municipality_id` is the município the sale is in — the one picked from
        `list_sold_territory`. Each polygon needs a vertex inside it and
        `min_shared_municipality_pct` of its area there; None uses the
        deployment's minimum, and `thresholds` says which was used.

        A group that fails a rule is an ANSWER, not an error: `valid` is False
        and `errors` says why. `pairs` holds the distance between each two
        polygons, `shared_municipality.per_polygon_pct` each polygon's share
        inside the município. One polygon is a group of one: no pair to
        measure, and the município rule still answers.

        Raises `UnprocessableError` for what is not a group at all: no polygon
        or more than the deployment allows (`groups.validate.polygon_count`),
        or an IBGE code that does not exist
        (`groups.validate.unknown_municipality`).
        """
        return await self._groups.validate(
            polygons,
            municipality_id=municipality_id,
            min_shared_municipality_pct=min_shared_municipality_pct,
        )

    async def resolve_rates(
        self,
        polygons: Sequence[GeometryInput],
        *,
        season_id: int,
        product_id: int,
        deductible_id: int,
    ) -> RateResolutionPolygonsResponse:
        """What the sale costs: the rate of every polygon, and of the sale.

        `season_id` is the safra being sold; `product_id` and `deductible_id`
        are the produto and the franquia the buyer picked from
        `list_products_on_sale`.

        The answer's `aggregate_value` is the COMMERCIAL rate of the whole sale
        and `aggregate_risk_value` its risk rate, both in the unit the rates
        were written in (13.19 is 13.19%), weighted by area over every polygon;
        `area_ha` is all the ground. `aggregate_expected_yield_kg_ha` is None
        unless every polygon states a yield. `polygons` holds the same for each
        polygon, in the order given, with the `layers` that priced it — each
        área, its rates and how much ground it priced — and the `run_id` that
        pins that polygon's answer (`gis.rates.get_run`).

        Each polygon is resolved on the finest grid its size allows; its
        `cell_m` says which.

        ALL OR NOTHING: a polygon that cannot be resolved raises
        `PolygonsRefusedError`, and nothing was resolved. Its `refusals` name
        every polygon that failed and why — `RateRefusalCode` lists the reasons.

        What is wrong with the request itself, and not with a polygon, raises
        `UnprocessableError` before any polygon is read: a safra that does not
        sell the produto (`rates.write.product_not_in_season` — also what an id
        naming nothing answers), a franquia the safra has no fator for
        (`rates.resolve.no_layer_for_franquia`), no polygon or more than the
        deployment resolves at once (`rates.resolve.polygon_count`), or a
        polygon that cannot be read (`geometry.invalid`, with `polygon_index`).
        """
        return await self._rates.resolve_polygons(
            polygons,
            season_id=season_id,
            product_id=product_id,
            deductible_id=deductible_id,
        )

    async def screen_car_properties(self, car_codes: Sequence[str]) -> ScreeningResponse:
        """What the registries hold on the CAR imóveis of a contract.

        `car_codes` are the codes picked from `list_car_properties`. One result
        per code, in the order given: the registration as SICAR holds it and
        every registry feature that intersects the imóvel — embargoes,
        conservation units, indigenous land and the rest — with how much of the
        imóvel each covers and the article of the norm it pertains to. It
        REPORTS and never decides: there is no verdict in the answer.

        A code the SICAR copy does not hold answers `outcome` `not_in_snapshot`
        for that code and does not fail the others. `sources` are the registry
        copies read, `not_covered` what this platform does not check, and
        `run_id` pins the answer so it can be cited and found again
        (`gis.screening.get_run`). No code at all raises `UnprocessableError`
        (`screening.screen.no_properties_requested`).
        """
        return await self._screening.screen(
            ScreeningRequest(items=[ScreeningItemRequest(cod_imovel=code) for code in car_codes])
        )

    async def screen_polygons(self, polygons: Sequence[GeometryInput]) -> OverlapsPolygonsResponse:
        """What the registries hold over the polygons of a contract themselves.

        One entry per polygon, in the order given. `esg` is every registry
        feature that intersects the polygon, with how much OF THE POLYGON it
        covers (`overlap_ha`, `overlap_pct` — None for a point feature, which
        is located inside rather than covering) and the article of the norm it
        pertains to; `esg_covered_pct` is the share of the polygon under all of
        them together. `car` is the CAR imóveis over the polygon and the share
        they cover together.

        `sources` are the registry copies read, the same for every polygon. It
        REPORTS: nothing in the answer is a verdict, and nothing is pinned.
        """
        return await self._screening.overlaps_polygons(polygons)

    async def check_policy_overlap(
        self,
        polygons: Sequence[GeometryInput],
        *,
        product_id: int | None = None,
        season_ids: Sequence[int] | None = None,
        running_only: bool = True,
        planting_window_ids: Sequence[int] | None = None,
    ) -> PolicyOverlapPolygonsResponse:
        """Whether any polygon of a contract collides with a policy already sold.

        The question is narrowed by what the caller passes, once for every
        polygon:

        - `product_id` — only policies of that produto; None asks every produto.
        - `season_ids` — exactly those safras; None asks the safras open today.
        - `running_only` — False also asks policies that have ended.
        - `planting_window_ids` — only policies sold under those windows. A
          policy with no window is always asked: it covers the whole safra.

        `total_matches` counts the collisions over all the polygons: zero means
        none. `polygons` holds each polygon's `matches`, in the order given —
        the policy, its safra and produto, and how much OF THE POLYGON it covers.
        `checked_seasons` is what was actually asked, and
        `unchecked_undated_seasons` the live safras that could not be, because
        nobody dated them.

        A safra that does not exist raises `UnprocessableError`
        (`policies.overlap.unknown_season`).
        """
        return await self._policies.check_polygons_overlap(
            PolicyOverlapPolygonsRequest(
                geometries=[to_geojson(polygon) for polygon in polygons],
                product_id=product_id,
                season_ids=season_ids,
                running_only=running_only,
                planting_window_ids=planting_window_ids,
            )
        )


__all__ = ["Underwriting"]
