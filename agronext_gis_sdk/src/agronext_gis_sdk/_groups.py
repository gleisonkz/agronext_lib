"""Group evaluation (C-13): whether a set of polygons may be underwritten together
— or one polygon, against the município it is declared in."""

import enum
from collections.abc import Sequence

from agronext_gis_sdk._http import API_PREFIX, HttpClient
from agronext_gis_sdk._wire import (
    BoundingBox,
    GeoJson,
    GeometryInput,
    LonLat,
    WireModel,
    to_geojson,
)


class GroupPairStatus(enum.StrEnum):
    """How far apart one pair of polygons is."""

    OK = "ok"
    WARNING = "warning"
    TOO_FAR = "too_far"


class GroupThresholds(WireModel):
    """The numbers the verdict was reached with."""

    ok_distance_km: float
    max_distance_km: float
    max_polygons: int
    min_shared_municipality_pct: float


class GroupPolygonSummary(WireModel):
    """One submitted polygon, measured.

    The API calls this schema `PolygonSummary` inside its groups app; the SDK
    names it apart from the client tools' one.
    """

    geometry: GeoJson
    area_ha: float
    area_km2: float
    centroid: LonLat
    bbox: BoundingBox


class GroupPairItem(WireModel):
    """One pair of polygons, by index into the submitted order."""

    a: int
    b: int
    distance_km: float
    status: GroupPairStatus
    #: The closest-points line, EPSG:4326.
    segment: Sequence[LonLat]


class SharedMunicipalityItem(WireModel):
    """The município the whole group is anchored in."""

    id: int
    name: str
    state_abbr: str
    per_polygon_pct: Sequence[float]
    boundary: GeoJson


class GroupValidateRequest(WireModel):
    geometries: Sequence[GeoJson]
    #: The município the proposal declares, by IBGE code.
    municipality_id: int | None = None
    #: This request's minimum share (%) of each polygon inside the município.
    min_shared_municipality_pct: float | None = None


class GroupValidateResponse(WireModel):
    """The verdict, the evidence for it, and the thresholds it used."""

    valid: bool
    errors: Sequence[str]
    warnings: Sequence[str]
    polygons: Sequence[GroupPolygonSummary]
    pairs: Sequence[GroupPairItem]
    shared_municipality: SharedMunicipalityItem | None
    centroid: LonLat
    total_area_ha: float
    thresholds: GroupThresholds


class Groups:
    """`gis.groups` — the distance check between the polygons of one policy."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def validate(
        self,
        geometries: Sequence[GeometryInput],
        *,
        municipality_id: int | None = None,
        min_shared_municipality_pct: float | None = None,
    ) -> GroupValidateResponse:
        """Evaluate 1 to 12 polygons (C-13). A tool: it writes nothing.

        `municipality_id` (IBGE code) anchors the group in the município the
        proposal declares: each polygon needs a vertex in it and
        `min_shared_municipality_pct` of its area inside it. Without it, the
        município the polygons share is found. `min_shared_municipality_pct`
        None uses the deployment's setting; `thresholds` says which was used.
        An unknown code is refused (`groups.validate.unknown_municipality`).
        """
        return await self._http.model(
            GroupValidateResponse,
            "POST",
            f"{API_PREFIX}/groups/validate",
            body=GroupValidateRequest(
                geometries=[to_geojson(item) for item in geometries],
                municipality_id=municipality_id,
                min_shared_municipality_pct=min_shared_municipality_pct,
            ),
        )


__all__ = [
    "GroupPairItem",
    "GroupPairStatus",
    "GroupPolygonSummary",
    "GroupThresholds",
    "GroupValidateRequest",
    "GroupValidateResponse",
    "Groups",
    "SharedMunicipalityItem",
]
