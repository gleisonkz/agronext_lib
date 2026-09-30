"""The rates capability, in four namespaces: produtos, safras, each (safra,
produto)'s configuration, and the rates themselves.

The API keeps all of it in one app; the SDK splits it by what a caller is
working on, so `gis.pairs.save_scope(...)` reads as what it does.
"""

from collections.abc import Sequence

from agronext_gis_sdk._http import API_PREFIX, HttpClient
from agronext_gis_sdk._rates_models import (
    CarAdjustmentBatchRequest,
    CarAdjustmentBatchResponse,
    CarAdjustmentItem,
    CarAdjustmentWriteItem,
    ContestItem,
    ContestOrderRequest,
    DeductibleCreateRequest,
    DeductibleItem,
    DeductibleResponse,
    PairConfigurationResponse,
    PlantingWindowDeclaration,
    PlantingWindowItem,
    PlantingWindowsRequest,
    PricingRequest,
    PricingResponse,
    ProductCreateRequest,
    ProductItem,
    ProductResponse,
    ProductUpdateRequest,
    RateCellSummaryItem,
    RateHeatmapRequest,
    RateHeatmapResponse,
    RateItem,
    RateResolutionPreflightRequest,
    RateResolutionPreflightResponse,
    RateResolutionRequest,
    RateResolutionResponse,
    RateResolutionRunItem,
    RateResolutionRunResponse,
    RateWriteBatchItem,
    RateWriteBatchRequest,
    RateWriteBatchResponse,
    RateWriteItem,
    ScopeAreaItem,
    ScopeOutlineResponse,
    ScopePreviewResponse,
    ScopeRequest,
    ScopeResponse,
    ScopeSummaryResponse,
    SeasonCreateRequest,
    SeasonItem,
    SeasonProductsRequest,
    SeasonResponse,
    SeasonUpdateRequest,
    SeasonWithCopiesResponse,
    SoldTerritoryItem,
)
from agronext_gis_sdk._wire import GeometryInput, LayerLevel, Page, to_geojson

_RATES = f"{API_PREFIX}/rates"


class Products:
    """`gis.products` — produtos and their franquias."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list_products(self, *, include_retired: bool = False) -> list[ProductItem]:
        return await self._http.models(
            ProductItem,
            "GET",
            f"{_RATES}/products",
            query={"include_retired": include_retired},
        )

    async def create_product(self, request: ProductCreateRequest) -> ProductResponse:
        return await self._http.model(ProductResponse, "POST", f"{_RATES}/products", body=request)

    async def update_product(
        self, product_id: int, request: ProductUpdateRequest
    ) -> ProductResponse:
        """Name, crop, peril and `yield_required`. The code is the identity and
        does not change."""
        return await self._http.model(
            ProductResponse, "PUT", f"{_RATES}/products/{product_id}", body=request
        )

    async def retire_product(self, product_id: int) -> ProductResponse:
        return await self._http.model(
            ProductResponse, "POST", f"{_RATES}/products/{product_id}/retire"
        )

    async def list_product_seasons(
        self, product_id: int, *, include_retired: bool = False
    ) -> list[SeasonItem]:
        """The safras selling this produto, newest period first."""
        return await self._http.models(
            SeasonItem,
            "GET",
            f"{_RATES}/products/{product_id}/seasons",
            query={"include_retired": include_retired},
        )

    async def list_deductibles(
        self, product_id: int, *, include_retired: bool = False
    ) -> list[DeductibleItem]:
        """The produto's franquias."""
        return await self._http.models(
            DeductibleItem,
            "GET",
            f"{_RATES}/products/{product_id}/deductibles",
            query={"include_retired": include_retired},
        )

    async def create_deductible(
        self, product_id: int, request: DeductibleCreateRequest
    ) -> DeductibleResponse:
        return await self._http.model(
            DeductibleResponse,
            "POST",
            f"{_RATES}/products/{product_id}/deductibles",
            body=request,
        )

    async def retire_deductible(self, deductible_id: int) -> DeductibleResponse:
        return await self._http.model(
            DeductibleResponse, "POST", f"{_RATES}/deductibles/{deductible_id}/retire"
        )


class Seasons:
    """`gis.seasons` — safras, the produtos each sells, and copying between them."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list_seasons(self, *, include_retired: bool = False) -> list[SeasonItem]:
        """Newest period first."""
        return await self._http.models(
            SeasonItem, "GET", f"{_RATES}/seasons", query={"include_retired": include_retired}
        )

    async def list_open_seasons(self) -> list[SeasonItem]:
        """The safras running today."""
        return await self._http.models(SeasonItem, "GET", f"{_RATES}/seasons/open")

    async def latest_season(self) -> SeasonItem:
        """The live safra whose period starts last — what every call naming no safra uses."""
        return await self._http.model(SeasonItem, "GET", f"{_RATES}/seasons/latest")

    async def create_season(self, request: SeasonCreateRequest) -> SeasonWithCopiesResponse:
        """A safra with its produtos — and, with `copies`, those produtos copied
        from other safras in the same act (Duplicar)."""
        return await self._http.model(
            SeasonWithCopiesResponse, "POST", f"{_RATES}/seasons", body=request
        )

    async def update_season(self, season_id: int, request: SeasonUpdateRequest) -> SeasonResponse:
        """Label and period."""
        return await self._http.model(
            SeasonResponse, "PUT", f"{_RATES}/seasons/{season_id}", body=request
        )

    async def retire_season(self, season_id: int) -> SeasonResponse:
        return await self._http.model(
            SeasonResponse, "POST", f"{_RATES}/seasons/{season_id}/retire"
        )

    async def list_season_products(
        self, season_id: int, *, include_retired: bool = False
    ) -> list[ProductItem]:
        """The produtos this safra sells — the only ones a rate may be written for."""
        return await self._http.models(
            ProductItem,
            "GET",
            f"{_RATES}/seasons/{season_id}/products",
            query={"include_retired": include_retired},
        )

    async def set_season_products(
        self, season_id: int, request: SeasonProductsRequest
    ) -> SeasonWithCopiesResponse:
        """REPLACE the produtos this safra sells — and copy the ones in `copies`
        from other safras in the same save ("Copiar de")."""
        return await self._http.model(
            SeasonWithCopiesResponse,
            "PUT",
            f"{_RATES}/seasons/{season_id}/products",
            body=request,
        )


class Pairs:
    """`gis.pairs` — one (safra, produto): its abrangência, fatores, planting
    windows, bonificações/agravamentos and overlap order."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def configuration(self, season_id: int, product_id: int) -> PairConfigurationResponse:
        """What this pair holds, counted, and its planting windows."""
        return await self._http.model(
            PairConfigurationResponse, "GET", f"{_pair(season_id, product_id)}/configuration"
        )

    async def list_planting_windows(
        self, season_id: int, product_id: int, *, include_retired: bool = False
    ) -> list[PlantingWindowItem]:
        """Earliest first. None at all is ordinary: the whole safra is the period."""
        return await self._http.models(
            PlantingWindowItem,
            "GET",
            f"{_pair(season_id, product_id)}/planting-windows",
            query={"include_retired": include_retired},
        )

    async def set_planting_windows(
        self, season_id: int, product_id: int, windows: Sequence[PlantingWindowDeclaration]
    ) -> list[PlantingWindowItem]:
        """The WHOLE set: none, or two or more. Matched by label."""
        return await self._http.models(
            PlantingWindowItem,
            "PUT",
            f"{_pair(season_id, product_id)}/planting-windows",
            body=PlantingWindowsRequest(windows=windows),
        )

    async def pricing(self, season_id: int, product_id: int) -> PricingResponse:
        """The rate mode, and each franquia's fatores."""
        return await self._http.model(
            PricingResponse, "GET", f"{_pair(season_id, product_id)}/pricing"
        )

    async def set_pricing(
        self, season_id: int, product_id: int, request: PricingRequest
    ) -> PricingResponse:
        """The mode and the WHOLE fator table of the live franquias."""
        return await self._http.model(
            PricingResponse, "PUT", f"{_pair(season_id, product_id)}/pricing", body=request
        )

    async def list_adjustments(  # noqa: PLR0913 — the pair, then the listing's filters
        self,
        season_id: int,
        product_id: int,
        *,
        state_id: int | None = None,
        query: str | None = None,
        page: int = 1,
        size: int | None = None,
    ) -> Page[CarAdjustmentItem]:
        """The CAR imóveis carrying a bonificação or agravamento; `query` matches
        the CAR code."""
        return await self._http.model(
            Page[CarAdjustmentItem],
            "GET",
            f"{_pair(season_id, product_id)}/adjustments",
            query={"stateId": state_id, "query": query, "page": page, "size": size},
        )

    async def write_adjustments(
        self, season_id: int, product_id: int, request: CarAdjustmentBatchRequest
    ) -> CarAdjustmentBatchResponse:
        """Set or clear adjustments, as one act."""
        return await self._http.model(
            CarAdjustmentBatchResponse,
            "POST",
            f"{_pair(season_id, product_id)}/adjustments/writes",
            body=request,
        )

    async def list_adjustment_history(
        self, season_id: int, product_id: int, *, page: int = 1, size: int | None = None
    ) -> Page[CarAdjustmentWriteItem]:
        return await self._http.model(
            Page[CarAdjustmentWriteItem],
            "GET",
            f"{_pair(season_id, product_id)}/adjustments/history",
            query={"page": page, "size": size},
        )

    async def scope(self, season_id: int, product_id: int) -> ScopeResponse:
        """The abrangência as saved: the liberada and the proibida."""
        return await self._http.model(ScopeResponse, "GET", f"{_pair(season_id, product_id)}/scope")

    async def save_scope(
        self, season_id: int, product_id: int, request: ScopeRequest
    ) -> ScopeResponse:
        """SAVE both outlines from the áreas given. A smaller liberada removes the
        rates and adjustments it leaves outside, in the same act."""
        return await self._http.model(
            ScopeResponse, "PUT", f"{_pair(season_id, product_id)}/scope", body=request
        )

    async def preview_scope(
        self, season_id: int, product_id: int, request: ScopeRequest
    ) -> ScopePreviewResponse:
        """What `save_scope` would do with this request, without doing it."""
        return await self._http.model(
            ScopePreviewResponse,
            "POST",
            f"{_pair(season_id, product_id)}/scope/preview",
            body=request,
        )

    async def list_scope_areas(  # noqa: PLR0913 — the pair, then the listing's filters
        self,
        season_id: int,
        product_id: int,
        *,
        level: LayerLevel | None = None,
        state_id: int | None = None,
        query: str | None = None,
        ids: Sequence[int] | None = None,
        page: int = 1,
        size: int | None = None,
    ) -> Page[ScopeAreaItem]:
        """The catálogo áreas that overlap the liberada — the ones a rate may be
        written on. CAR imóveis one UF at a time."""
        return await self._http.model(
            Page[ScopeAreaItem],
            "GET",
            f"{_pair(season_id, product_id)}/scope/areas",
            query={
                "level": level,
                "stateId": state_id,
                "query": query,
                "ids": list(ids) if ids is not None else None,
                "page": page,
                "size": size,
            },
        )

    async def scope_outline(
        self,
        season_id: int,
        product_id: int,
        *,
        region_id: int | None = None,
        state_id: int | None = None,
        level: LayerLevel | None = None,
    ) -> ScopeOutlineResponse:
        """Where an Em massa act writes: a região's members, or a UF's áreas of
        one level, that the liberada reaches — counted, and unioned into one
        outline. Needs `region_id` or `state_id`."""
        return await self._http.model(
            ScopeOutlineResponse,
            "GET",
            f"{_pair(season_id, product_id)}/scope/outline",
            query={"regionId": region_id, "stateId": state_id, "level": level},
        )

    async def scope_summary(
        self, season_id: int, product_id: int, *, state_id: int | None = None
    ) -> ScopeSummaryResponse:
        """How many catálogo áreas the liberada reaches per level, and its UFs."""
        return await self._http.model(
            ScopeSummaryResponse,
            "GET",
            f"{_pair(season_id, product_id)}/scope/summary",
            query={"stateId": state_id},
        )

    async def territory(self, season_id: int, product_id: int) -> list[SoldTerritoryItem]:
        """Where this produto can be sold: UFs and their priced municípios."""
        return await self._http.models(
            SoldTerritoryItem, "GET", f"{_pair(season_id, product_id)}/territory"
        )

    async def list_contests(self, season_id: int, product_id: int) -> list[ContestItem]:
        """Where custom polygons cover the same ground, and who wins there."""
        return await self._http.models(
            ContestItem, "GET", f"{_pair(season_id, product_id)}/contests"
        )

    async def order_contest(
        self, season_id: int, product_id: int, contest_id: int, area_ids: Sequence[int]
    ) -> list[ContestItem]:
        """Put one contest's members in this order — the same members. First wins."""
        return await self._http.models(
            ContestItem,
            "PUT",
            f"{_pair(season_id, product_id)}/contests/{contest_id}",
            body=ContestOrderRequest(area_ids=area_ids),
        )


class Rates:
    """`gis.rates` — the rates written, their trail, and resolving them over a polygon."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list_rates(  # noqa: PLR0913 — the célula, then the listing's filters
        self,
        *,
        product_id: int,
        season_id: int | None = None,
        deductible_id: int | None = None,
        reference: bool = False,
        level: LayerLevel | None = None,
        area_id: int | None = None,
        state_id: int | None = None,
        page: int = 1,
        size: int | None = None,
    ) -> Page[RateItem]:
        """The rates that EXIST in one layer: a franquia's (`deductible_id`) or the
        reference layer (`reference=True`) — exactly one of the two."""
        return await self._http.model(
            Page[RateItem],
            "GET",
            _RATES,
            query={
                "seasonId": season_id,
                "productId": product_id,
                "deductibleId": deductible_id,
                "reference": reference,
                "level": level,
                "areaId": area_id,
                "stateId": state_id,
                "page": page,
                "size": size,
            },
        )

    async def coverage(
        self,
        *,
        season_id: int,
        product_id: int,
        deductible_id: int | None = None,
        reference: bool = False,
    ) -> list[RateCellSummaryItem]:
        """What one layer holds right now, per level."""
        return await self._http.models(
            RateCellSummaryItem,
            "GET",
            f"{_RATES}/coverage",
            query={
                "seasonId": season_id,
                "productId": product_id,
                "deductibleId": deductible_id,
                "reference": reference,
            },
        )

    async def write(self, request: RateWriteBatchRequest) -> RateWriteBatchResponse:
        """ONE act: every operation lands, or none does; each is a trail row."""
        return await self._http.model(
            RateWriteBatchResponse, "POST", f"{_RATES}/writes", body=request
        )

    async def list_writes(  # noqa: PLR0913 — the trail's filters, all keyword-only
        self,
        *,
        season_id: int | None = None,
        product_id: int | None = None,
        deductible_id: int | None = None,
        reference: bool = False,
        area_id: int | None = None,
        user_id: int | None = None,
        batch_id: int | None = None,
        page: int = 1,
        size: int | None = None,
    ) -> Page[RateWriteItem]:
        """The rate trail, a row per write, newest first."""
        return await self._http.model(
            Page[RateWriteItem],
            "GET",
            f"{_RATES}/history",
            query={
                "seasonId": season_id,
                "productId": product_id,
                "deductibleId": deductible_id,
                "reference": reference,
                "areaId": area_id,
                "userId": user_id,
                "batchId": batch_id,
                "page": page,
                "size": size,
            },
        )

    async def list_write_batches(  # noqa: PLR0913 — the trail's filters, all keyword-only
        self,
        *,
        user_id: int | None = None,
        season_id: int | None = None,
        product_id: int | None = None,
        deductible_id: int | None = None,
        reference: bool = False,
        page: int = 1,
        size: int | None = None,
    ) -> Page[RateWriteBatchItem]:
        """The trail a row per act: what one person changed on one occasion."""
        return await self._http.model(
            Page[RateWriteBatchItem],
            "GET",
            f"{_RATES}/history/batches",
            query={
                "userId": user_id,
                "seasonId": season_id,
                "productId": product_id,
                "deductibleId": deductible_id,
                "reference": reference,
                "page": page,
                "size": size,
            },
        )

    async def preflight(
        self, geometry: GeometryInput, *, cell_m: int | None = None
    ) -> RateResolutionPreflightResponse:
        """Which grid resolutions this polygon can be resolved at — before any work."""
        return await self._http.model(
            RateResolutionPreflightResponse,
            "POST",
            f"{_RATES}/resolve/preflight",
            body=RateResolutionPreflightRequest(geometry=to_geojson(geometry), cell_m=cell_m),
        )

    async def resolve(
        self,
        geometry: GeometryInput,
        *,
        product_id: int,
        deductible_id: int,
        cell_m: int,
        season_id: int | None = None,
    ) -> RateResolutionResponse:
        """The rate over a polygon: per tile, and area-weighted. Pins a run.
        `season_id` None resolves in the latest safra."""
        return await self._http.model(
            RateResolutionResponse,
            "POST",
            f"{_RATES}/resolve",
            body=RateResolutionRequest(
                geometry=to_geojson(geometry),
                season_id=season_id,
                product_id=product_id,
                deductible_id=deductible_id,
                cell_m=cell_m,
            ),
        )

    async def heatmap(self, request: RateHeatmapRequest) -> RateHeatmapResponse:
        """One franquia's rate surface over the liberada inside a bounding box."""
        return await self._http.model(
            RateHeatmapResponse, "POST", f"{_RATES}/heatmap", body=request
        )

    async def list_runs(  # noqa: PLR0913 — the listing's filters, all keyword-only
        self,
        *,
        user_id: int | None = None,
        season_id: int | None = None,
        product_id: int | None = None,
        deductible_id: int | None = None,
        page: int = 1,
        size: int | None = None,
    ) -> Page[RateResolutionRunItem]:
        """The pinned resolutions, newest first."""
        return await self._http.model(
            Page[RateResolutionRunItem],
            "GET",
            f"{_RATES}/runs",
            query={
                "userId": user_id,
                "seasonId": season_id,
                "productId": product_id,
                "deductibleId": deductible_id,
                "page": page,
                "size": size,
            },
        )

    async def get_run(self, run_id: int) -> RateResolutionRunResponse:
        """One pinned resolution, with the polygon that produced it."""
        return await self._http.model(RateResolutionRunResponse, "GET", f"{_RATES}/runs/{run_id}")


def _pair(season_id: int, product_id: int) -> str:
    return f"{_RATES}/seasons/{season_id}/products/{product_id}"


__all__ = ["Pairs", "Products", "Rates", "Seasons"]
