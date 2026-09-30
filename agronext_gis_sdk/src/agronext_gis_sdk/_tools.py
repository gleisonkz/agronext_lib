"""Client tools: KML in and out, and measuring a polygon properly."""

from collections.abc import Sequence
from typing import Final

from agronext_gis_sdk._http import API_PREFIX, HttpClient
from agronext_gis_sdk._wire import (
    BoundingBox,
    GeoJson,
    GeometryInput,
    LonLat,
    WireModel,
    to_geojson,
)

_TOOLS = f"{API_PREFIX}/client-tools"

#: The multipart field the KML endpoints read the file from.
_KML_FIELD: Final[str] = "file"
#: What a KML upload is sent as.
KML_MEDIA_TYPE: Final[str] = "application/vnd.google-earth.kml+xml"


class PolygonSummary(WireModel):
    """One polygon, measured in a metric projection and returned in EPSG:4326."""

    geometry: GeoJson
    area_ha: float
    area_km2: float
    centroid: LonLat
    bbox: BoundingBox


class KmlImportResponse(WireModel):
    polygons: Sequence[PolygonSummary]
    count: int


class NamedPolygonRequest(WireModel):
    name: str | None = None
    geometry: GeoJson


class KmlExportRequest(WireModel):
    document_name: str | None = None
    polygons: Sequence[NamedPolygonRequest]


class PolygonSummaryRequest(WireModel):
    geometry: GeoJson


class Tools:
    """`gis.tools` — KML import and export, and polygon measurement."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def import_kml_polygon(
        self, content: bytes, *, filename: str = "area.kml"
    ) -> PolygonSummary:
        """One polygon out of a .kml document — the area a screening or a resolution takes."""
        return await self._http.model(
            PolygonSummary,
            "POST",
            f"{_TOOLS}/kml/polygon",
            files={_KML_FIELD: (filename, content, KML_MEDIA_TYPE)},
        )

    async def import_kml_polygons(
        self, content: bytes, *, filename: str = "areas.kml"
    ) -> KmlImportResponse:
        """Every polygon of a .kml document — a group's."""
        return await self._http.model(
            KmlImportResponse,
            "POST",
            f"{_TOOLS}/kml/polygons",
            files={_KML_FIELD: (filename, content, KML_MEDIA_TYPE)},
        )

    async def export_kml(self, request: KmlExportRequest) -> bytes:
        """A set of polygons as one KML document; the answer is the file's bytes."""
        return await self._http.content("POST", f"{_TOOLS}/kml/export", body=request)

    async def summarise_polygon(self, geometry: GeometryInput) -> PolygonSummary:
        """Area in hectares (measured in a metric projection), centroid and bounding box."""
        return await self._http.model(
            PolygonSummary,
            "POST",
            f"{_TOOLS}/polygon/summary",
            body=PolygonSummaryRequest(geometry=to_geojson(geometry)),
        )


__all__ = [
    "KML_MEDIA_TYPE",
    "KmlExportRequest",
    "KmlImportResponse",
    "NamedPolygonRequest",
    "PolygonSummary",
    "PolygonSummaryRequest",
    "Tools",
]
