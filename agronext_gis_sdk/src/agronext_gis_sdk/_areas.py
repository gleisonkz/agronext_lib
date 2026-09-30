"""The área catalogue — every polygon a rate can be written to — and regiões."""

import datetime
import decimal
import uuid
from collections.abc import Sequence

from agronext_gis_sdk._http import API_PREFIX, HttpClient, QueryValue
from agronext_gis_sdk._wire import (
    GeoJson,
    GeometryInput,
    LayerLevel,
    LayerRevisionOperation,
    Page,
    ScopeList,
    WireModel,
    to_geojson,
)

_AREAS = f"{API_PREFIX}/areas"
_REGIONS = f"{API_PREFIX}/regions"
_FOLDERS = f"{API_PREFIX}/region-folders"


class AreaItem(WireModel):
    """An área in a listing: everything but the geometry."""

    id: int
    level: LayerLevel
    name: str | None = None
    #: OUR reference for it ('MT-NORTE-01'); None until somebody sets one.
    code: str | None = None
    #: Who published the geometry: 'IBGE', 'SICAR', or None for a drawn one.
    source_name: str | None = None
    #: The publisher's own id: the IBGE code, or the CAR `cod_imovel`.
    source_id: str | None = None
    country_id: int | None = None
    state_id: int | None = None
    municipality_id: int | None = None
    state_abbr: str | None = None
    area_ha: float
    retired_at: datetime.datetime | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime


class AreaResponse(AreaItem):
    """One área, with its geometry."""

    geometry: GeoJson
    source_boundary_snapshot_id: int | None = None
    created_by_username: str | None = None


class AreaIdList(WireModel):
    """The ids matching a filter; `truncated` when there were more than served."""

    area_ids: Sequence[int]
    total: int
    truncated: bool


class AreaPricedCellItem(WireModel):
    season_label: str
    product_code: str
    #: None: the reference layer.
    deductible: decimal.Decimal | None = None


class AreaScopePieceItem(WireModel):
    season_label: str
    product_code: str
    outline: ScopeList


class AreaUsageResponse(WireModel):
    """What redrawing this área would change: where it is priced, and the
    abrangências built from it (which keep the outline they saved)."""

    priced: Sequence[AreaPricedCellItem] = ()
    scopes: Sequence[AreaScopePieceItem] = ()


class CustomAreaCreateRequest(WireModel):
    """A drawn or uploaded polygon becoming a custom área."""

    name: str
    code: str | None = None
    geometry: GeoJson


class CustomAreaUpdateRequest(WireModel):
    """Rename, re-code or re-draw a custom área. A field left unset is left as is."""

    name: str | None = None
    code: str | None = None
    geometry: GeoJson | None = None


class AreaRevisionItem(WireModel):
    """One entry of an área's history."""

    id: int
    operation: LayerRevisionOperation
    level: LayerLevel
    name: str | None = None
    recorded_at: datetime.datetime
    recorded_by_username: str | None = None
    correlation_id: uuid.UUID
    source_boundary_snapshot_id: int | None = None


class RegionItem(WireModel):
    """A região: a named set of áreas of ONE level."""

    id: int
    name: str
    code: str | None = None
    area_level: LayerLevel
    area_count: int
    retired_at: datetime.datetime | None = None
    #: The pasta it is filed in; both None is "Sem pasta".
    folder_id: int | None = None
    folder_name: str | None = None


class RegionResponse(RegionItem):
    area_ids: Sequence[int]


class RegionCreateRequest(WireModel):
    name: str
    code: str | None = None
    area_level: LayerLevel
    #: The pasta to file it in; None is "Sem pasta". The name must be free
    #: among that pasta's live regions.
    folder_id: int | None = None
    area_ids: Sequence[int] = ()


class RegionUpdateRequest(WireModel):
    """Rename, re-code, move to another pasta. The level is fixed at creation.
    The whole form: `code` None clears it, `folder_id` None is "Sem pasta" —
    send the region's current pasta to keep it."""

    name: str
    code: str | None = None
    folder_id: int | None = None


class RegionMembershipRequest(WireModel):
    """The WHOLE membership: ids left out are removed."""

    area_ids: Sequence[int]


class Areas:
    """`gis.areas` — the catálogo of áreas, at every level."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list_areas(  # noqa: PLR0913 — the listing's filters, all keyword-only
        self,
        *,
        level: LayerLevel | None = None,
        levels: Sequence[LayerLevel] | None = None,
        state_id: int | None = None,
        municipality_id: int | None = None,
        query: str | None = None,
        ids: Sequence[int] | None = None,
        include_retired: bool = False,
        retired_only: bool = False,
        page: int = 1,
        size: int | None = None,
    ) -> Page[AreaItem]:
        """The catálogo, filtered; CAR imóveis one UF at a time. `retired_only`
        lists the disabled áreas alone."""
        return await self._http.model(
            Page[AreaItem],
            "GET",
            _AREAS,
            query=_area_filter(
                level=level,
                levels=levels,
                state_id=state_id,
                municipality_id=municipality_id,
                query=query,
                ids=ids,
                include_retired=include_retired,
                retired_only=retired_only,
            )
            | {"page": page, "size": size},
        )

    async def list_area_ids(  # noqa: PLR0913 — the listing's filters, all keyword-only
        self,
        *,
        level: LayerLevel | None = None,
        levels: Sequence[LayerLevel] | None = None,
        state_id: int | None = None,
        municipality_id: int | None = None,
        query: str | None = None,
        ids: Sequence[int] | None = None,
        include_retired: bool = False,
        retired_only: bool = False,
    ) -> AreaIdList:
        """The ids of the SET a filter matches — for acting on all of it at once."""
        return await self._http.model(
            AreaIdList,
            "GET",
            f"{_AREAS}/ids",
            query=_area_filter(
                level=level,
                levels=levels,
                state_id=state_id,
                municipality_id=municipality_id,
                query=query,
                ids=ids,
                include_retired=include_retired,
                retired_only=retired_only,
            ),
        )

    async def get_area(self, area_id: int) -> AreaResponse:
        return await self._http.model(AreaResponse, "GET", f"{_AREAS}/{area_id}")

    async def create_area(
        self, name: str, geometry: GeometryInput, *, code: str | None = None
    ) -> AreaResponse:
        """A drawn or uploaded polygon, saved as a custom área."""
        return await self._http.model(
            AreaResponse,
            "POST",
            _AREAS,
            body=CustomAreaCreateRequest(name=name, code=code, geometry=to_geojson(geometry)),
        )

    async def update_area(self, area_id: int, request: CustomAreaUpdateRequest) -> AreaResponse:
        """Rename, re-code or re-draw a custom área; each change is a revision."""
        return await self._http.model(AreaResponse, "PATCH", f"{_AREAS}/{area_id}", body=request)

    async def retire_area(self, area_id: int) -> AreaResponse:
        """Out of every choice from now on; what already uses it keeps working."""
        return await self._http.model(AreaResponse, "POST", f"{_AREAS}/{area_id}/retire")

    async def area_usage(self, area_id: int) -> AreaUsageResponse:
        """What a redraw of this área would change, asked before it is saved."""
        return await self._http.model(AreaUsageResponse, "GET", f"{_AREAS}/{area_id}/usage")

    async def list_area_revisions(
        self, area_id: int, *, page: int = 1, size: int | None = None
    ) -> Page[AreaRevisionItem]:
        return await self._http.model(
            Page[AreaRevisionItem],
            "GET",
            f"{_AREAS}/{area_id}/revisions",
            query={"page": page, "size": size},
        )


class RegionFolderItem(WireModel):
    """A pasta — how regions are filed, and nothing more — with its live count."""

    id: int
    name: str
    region_count: int


class RegionFolderList(WireModel):
    """Every pasta by name, and how many live regions are in none."""

    items: Sequence[RegionFolderItem]
    unfiled_count: int


class RegionFolderRequest(WireModel):
    name: str


class Regions:
    """`gis.regions` — named sets of áreas of one level, filed in pastas."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list_regions(  # noqa: PLR0913 — the listing's filters, all keyword-only
        self,
        *,
        include_retired: bool = False,
        retired_only: bool = False,
        folder_id: int | None = None,
        unfiled: bool = False,
        page: int = 1,
        size: int | None = None,
    ) -> Page[RegionItem]:
        """Live regions by pasta then name; with `include_retired` the disabled
        ones too, with `retired_only` the disabled ones alone. `folder_id`
        narrows to one pasta, `unfiled` to the regions in none."""
        return await self._http.model(
            Page[RegionItem],
            "GET",
            _REGIONS,
            query={
                "includeRetired": include_retired,
                "retiredOnly": retired_only,
                "folderId": folder_id,
                "unfiled": unfiled,
                "page": page,
                "size": size,
            },
        )

    async def create_region(self, request: RegionCreateRequest) -> RegionResponse:
        return await self._http.model(RegionResponse, "POST", _REGIONS, body=request)

    async def get_region(self, region_id: int) -> RegionResponse:
        return await self._http.model(RegionResponse, "GET", f"{_REGIONS}/{region_id}")

    async def update_region(self, region_id: int, request: RegionUpdateRequest) -> RegionResponse:
        return await self._http.model(
            RegionResponse, "PUT", f"{_REGIONS}/{region_id}", body=request
        )

    async def set_region_areas(self, region_id: int, area_ids: Sequence[int]) -> RegionResponse:
        """REPLACE the membership with exactly these áreas."""
        return await self._http.model(
            RegionResponse,
            "PUT",
            f"{_REGIONS}/{region_id}/areas",
            body=RegionMembershipRequest(area_ids=area_ids),
        )

    async def retire_region(self, region_id: int) -> RegionResponse:
        return await self._http.model(RegionResponse, "POST", f"{_REGIONS}/{region_id}/retire")

    async def list_folders(self) -> RegionFolderList:
        """Every pasta by name, with live counts."""
        return await self._http.model(RegionFolderList, "GET", _FOLDERS)

    async def create_folder(self, name: str) -> RegionFolderItem:
        return await self._http.model(
            RegionFolderItem, "POST", _FOLDERS, body=RegionFolderRequest(name=name)
        )

    async def rename_folder(self, folder_id: int, name: str) -> RegionFolderItem:
        return await self._http.model(
            RegionFolderItem, "PUT", f"{_FOLDERS}/{folder_id}", body=RegionFolderRequest(name=name)
        )

    async def delete_folder(self, folder_id: int) -> None:
        """Delete a pasta no live region is filed in; a disabled one left in it
        falls back to "Sem pasta"."""
        await self._http.nothing("DELETE", f"{_FOLDERS}/{folder_id}")


def _area_filter(  # noqa: PLR0913 — the catálogo's filters, all keyword-only
    *,
    level: LayerLevel | None,
    levels: Sequence[LayerLevel] | None,
    state_id: int | None,
    municipality_id: int | None,
    query: str | None,
    ids: Sequence[int] | None,
    include_retired: bool,
    retired_only: bool,
) -> dict[str, QueryValue]:
    return {
        "level": level,
        "levels": list(levels) if levels is not None else None,
        "stateId": state_id,
        "municipalityId": municipality_id,
        "query": query,
        "ids": list(ids) if ids is not None else None,
        "includeRetired": include_retired,
        "retiredOnly": retired_only,
    }


__all__ = [
    "AreaIdList",
    "AreaItem",
    "AreaPricedCellItem",
    "AreaResponse",
    "AreaRevisionItem",
    "AreaScopePieceItem",
    "AreaUsageResponse",
    "Areas",
    "CustomAreaCreateRequest",
    "CustomAreaUpdateRequest",
    "RegionCreateRequest",
    "RegionFolderItem",
    "RegionFolderList",
    "RegionFolderRequest",
    "RegionItem",
    "RegionMembershipRequest",
    "RegionResponse",
    "RegionUpdateRequest",
    "Regions",
]
