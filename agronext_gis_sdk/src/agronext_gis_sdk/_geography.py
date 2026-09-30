"""The administrative hierarchy (country → UF → município) and boundary lookups."""

from collections.abc import Sequence

from agronext_gis_sdk._http import API_PREFIX, HttpClient
from agronext_gis_sdk._wire import (
    GeoJson,
    GeometryInput,
    LayerLevel,
    LonLat,
    Page,
    SnapshotReference,
    WireModel,
    to_geojson,
)

_GEOGRAPHY = f"{API_PREFIX}/geography"


class CountryResponse(WireModel):
    id: int
    abbr: str
    name: str
    area_ha: float
    snapshot: SnapshotReference


class StateItem(WireModel):
    """One UF. `boundary` only when the listing was asked for geometry."""

    id: int
    abbr: str
    name: str
    municipality_count: int
    boundary: GeoJson | None = None


class StateResponse(WireModel):
    id: int
    abbr: str
    name: str
    boundary: GeoJson
    area_ha: float
    centroid: LonLat
    snapshot: SnapshotReference


class MunicipalityItem(WireModel):
    id: int
    name: str
    state_id: int
    state_abbr: str
    centroid: LonLat


class MunicipalityResponse(WireModel):
    """One município with its boundary. `patched_polygon`: the loader repaired
    the published IBGE polygon, so this is not the published one."""

    id: int
    name: str
    state_id: int
    state_abbr: str
    centroid: LonLat
    boundary: GeoJson
    area_ha: float
    patched_polygon: bool
    snapshot: SnapshotReference


class CountryRef(WireModel):
    id: int
    abbr: str
    name: str


class StateRef(WireModel):
    id: int
    abbr: str
    name: str


class MunicipalityRef(WireModel):
    id: int
    name: str
    state_id: int
    state_abbr: str


class MunicipalityShareItem(WireModel):
    """How much of the located geometry one município holds."""

    id: int
    name: str
    state_abbr: str
    share_pct: float
    overlap_ha: float


class LocateRequest(WireModel):
    geometry: GeoJson


class LocateResponse(WireModel):
    """Where a geometry falls. `municipality` is the largest share (or the one
    holding a pin); `level_resolved` is the deepest level that answered."""

    country: CountryRef
    state: StateRef | None
    municipality: MunicipalityRef | None
    municipalities: Sequence[MunicipalityShareItem]
    level_resolved: LayerLevel


class Geography:
    """`gis.geography` — Brazil, its UFs and municípios, and where a geometry falls."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def country(self) -> CountryResponse:
        return await self._http.model(CountryResponse, "GET", f"{_GEOGRAPHY}/country")

    async def list_states(self, *, include_geometry: bool = False) -> list[StateItem]:
        """The 27 UFs by name; with their boundaries when `include_geometry`."""
        return await self._http.models(
            StateItem,
            "GET",
            f"{_GEOGRAPHY}/states",
            query={"include_geometry": include_geometry},
        )

    async def get_state(self, state_id: int) -> StateResponse:
        return await self._http.model(StateResponse, "GET", f"{_GEOGRAPHY}/states/{state_id}")

    async def list_state_municipalities(self, state_id: int) -> list[MunicipalityItem]:
        """Every município of one UF, by name."""
        return await self._http.models(
            MunicipalityItem, "GET", f"{_GEOGRAPHY}/states/{state_id}/municipalities"
        )

    async def list_municipalities(
        self,
        *,
        query: str | None = None,
        state_id: int | None = None,
        page: int = 1,
        size: int | None = None,
    ) -> Page[MunicipalityItem]:
        """Across all UFs, paged; `query` matches anywhere in the name."""
        return await self._http.model(
            Page[MunicipalityItem],
            "GET",
            f"{_GEOGRAPHY}/municipalities",
            query={"query": query, "stateId": state_id, "page": page, "size": size},
        )

    async def get_municipality(self, municipality_id: int) -> MunicipalityResponse:
        return await self._http.model(
            MunicipalityResponse, "GET", f"{_GEOGRAPHY}/municipalities/{municipality_id}"
        )

    async def locate(self, geometry: GeometryInput) -> LocateResponse:
        """Which country, UF and município a drawn area or a dropped pin is in."""
        return await self._http.model(
            LocateResponse,
            "POST",
            f"{_GEOGRAPHY}/locate",
            body=LocateRequest(geometry=to_geojson(geometry)),
        )


__all__ = [
    "CountryRef",
    "CountryResponse",
    "Geography",
    "LocateRequest",
    "LocateResponse",
    "MunicipalityItem",
    "MunicipalityRef",
    "MunicipalityResponse",
    "MunicipalityShareItem",
    "StateItem",
    "StateRef",
    "StateResponse",
]
