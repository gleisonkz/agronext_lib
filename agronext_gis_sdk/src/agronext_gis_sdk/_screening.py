"""Screening: what the socio-environmental registries say about a piece of land.

It REPORTS and never decides — whether a finding blocks a sale is the caller's
judgement.
"""

import enum
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from agronext_gis_sdk._http import API_PREFIX, HttpClient
from agronext_gis_sdk._wire import (
    BrazilianState,
    GeoJson,
    GeometryInput,
    Page,
    RegistryKind,
    RunKind,
    SnapshotReference,
    WireModel,
    to_geojson,
)

_SCREENING = f"{API_PREFIX}/screening"


class ScreeningOutcome(enum.StrEnum):
    """Per item, so one unknown CAR code never fails a batch."""

    SCREENED = "screened"
    NOT_IN_SNAPSHOT = "not_in_snapshot"


class FindingMeasuredAgainst(enum.StrEnum):
    """What a finding's percentage is taken against."""

    PROPERTY = "imovel"
    INSURED_AREA = "area_segurada"


class NormReferenceRef(WireModel):
    """Where to read about a finding — never a conclusion."""

    article: str
    qualifier: str | None = None


class ScreeningCandidate(WireModel):
    """A CAR imóvel intersecting the area asked about, which the caller may screen."""

    area_id: int
    cod_imovel: str
    status: str | None = None
    status_label: str | None = None
    condition: str | None = None
    property_type: str | None = None
    area_ha: float | None = None
    municipality_id: int | None = None
    municipality: str | None = None
    state: str | None = None
    #: How much of the area asked about the imóvel covers, and as a share of it.
    overlap_ha: float
    overlap_pct: float
    geometry: GeoJson


class ScreeningPreflightRequest(WireModel):
    geometry: GeoJson
    limit: int | None = None


class ScreeningPreflightResponse(WireModel):
    total: int
    candidates: Sequence[ScreeningCandidate]
    car_snapshot: SnapshotReference


class ScreeningItemRequest(WireModel):
    """One imóvel to screen, and optionally the insured area inside it."""

    cod_imovel: str
    area_segurada: GeoJson | None = None


class ScreeningRequest(WireModel):
    """The imóveis to screen; `as_of` replays the registries at a past instant."""

    items: Sequence[ScreeningItemRequest]
    as_of: datetime | None = None


class ScreeningProperty(WireModel):
    """The CAR registration as held, verbatim."""

    cod_imovel: str
    status: str | None = None
    status_label: str | None = None
    condition: str | None = None
    property_type: str | None = None
    area_ha: float | None = None
    geometry_area_ha: float | None = None
    fiscal_modules: float | None = None
    municipality_id: int | None = None
    municipality: str | None = None
    state: str | None = None
    geometry: GeoJson


class ScreeningFinding(WireModel):
    """One intersecting registry feature, as held."""

    source: str
    dataset: str
    category: str
    name: str | None = None
    properties: Mapping[str, Any]
    overlap_ha: float | None = None
    overlap_pct: float | None = None
    geometry: GeoJson | None = None
    measured_against: FindingMeasuredAgainst
    norm_reference: NormReferenceRef | None = None
    supplementary: bool = False
    observed_at: date | None = None


class ScreeningCoverage(WireModel):
    """What was consulted for the imóvel's UF — so silence is readable."""

    state: str | None = None
    consulted: Sequence[str]
    supplementary: Sequence[str]
    state_enforcement_sources: Sequence[str]
    state_enforcement_note: str


class ScreeningResult(WireModel):
    cod_imovel: str
    outcome: ScreeningOutcome
    property: ScreeningProperty | None = None
    findings: Sequence[ScreeningFinding] = ()
    coverage: ScreeningCoverage | None = None
    area_segurada_ha: float | None = None
    note: str | None = None


class ScreeningResponse(WireModel):
    """One pinned screening (`run_id`), the sources it read, and what it does not check."""

    run_id: int
    generated_at: datetime
    as_of: datetime
    results: Sequence[ScreeningResult]
    sources: Sequence[SnapshotReference]
    not_covered: Sequence[str]
    disclaimer: str


class CoverageStatementResponse(WireModel):
    """What this platform does NOT check, readable before a screening runs."""

    statements: Sequence[str]
    disclaimer: str
    as_of: datetime


class OverlapsRequest(WireModel):
    geometry: GeoJson
    limit: int | None = None


class CarOverlapItem(WireModel):
    cod_imovel: str
    status: str | None = None
    condition: str | None = None
    property_type: str | None = None
    area_ha: float | None = None
    municipality: str | None = None
    overlap_ha: float
    overlap_pct: float
    geometry: GeoJson


class CarOverlaps(WireModel):
    total: int
    covered_pct: float
    items: Sequence[CarOverlapItem]


class EsgOverlapItem(WireModel):
    source: str
    dataset: str
    category: str
    name: str | None = None
    properties: Mapping[str, Any]
    overlap_ha: float | None = None
    overlap_pct: float | None = None
    geometry: GeoJson | None = None
    norm_reference: NormReferenceRef | None = None
    supplementary: bool = False


class OverlapsResponse(WireModel):
    """CAR imóveis and restriction features over an arbitrary polygon."""

    car: CarOverlaps
    esg: Sequence[EsgOverlapItem]
    esg_covered_pct: float
    sources: Sequence[SnapshotReference]


class ScreeningRunItem(WireModel):
    id: int
    kind: RunKind
    requested_at: datetime
    as_of: datetime
    requested_by_username: str
    cell_m: int | None = None
    season_id: int | None = None
    product_id: int | None = None
    deductible_id: int | None = None
    aggregate_value: Decimal | None = None


class ScreeningRunResponse(WireModel):
    """One pinned run: the polygon, the instant, and which snapshots it read."""

    id: int
    kind: RunKind
    requested_at: datetime
    as_of: datetime
    requested_by_username: str
    query_polygon: GeoJson | None = None
    snapshots: Sequence[SnapshotReference]
    cell_m: int | None = None
    season_id: int | None = None
    product_id: int | None = None
    deductible_id: int | None = None
    tile_count: int | None = None
    unresolved_tile_count: int | None = None
    aggregate_value: Decimal | None = None


class Screening:
    """`gis.screening` — CAR imóveis, registry findings, and the runs that pinned them."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def preflight(
        self, geometry: GeometryInput, *, limit: int | None = None
    ) -> ScreeningPreflightResponse:
        """The CAR imóveis a drawn or imported AREA touches (C-2), each with how
        much of it it covers. A point is refused (`geometry.invalid`)."""
        return await self._http.model(
            ScreeningPreflightResponse,
            "POST",
            f"{_SCREENING}/preflight",
            body=ScreeningPreflightRequest(geometry=to_geojson(geometry), limit=limit),
        )

    async def screen(self, request: ScreeningRequest) -> ScreeningResponse:
        """Every registry feature intersecting each imóvel (C-3/C-4). Pins a run."""
        return await self._http.model(ScreeningResponse, "POST", _SCREENING, body=request)

    async def list_sources(
        self, *, kind: RegistryKind | None = None, state: BrazilianState | None = None
    ) -> list[SnapshotReference]:
        """Every registry source with the snapshot live now (C-5)."""
        return await self._http.models(
            SnapshotReference,
            "GET",
            f"{_SCREENING}/sources",
            query={"kind": kind, "state": state},
        )

    async def coverage_statement(
        self, *, as_of: datetime | None = None
    ) -> CoverageStatementResponse:
        """What is NOT checked — at a past instant when `as_of` is given."""
        return await self._http.model(
            CoverageStatementResponse,
            "GET",
            f"{_SCREENING}/coverage-statement",
            query={"asOf": as_of},
        )

    async def overlaps(
        self, geometry: GeometryInput, *, limit: int | None = None
    ) -> OverlapsResponse:
        """Registry features over an arbitrary polygon, with no imóvel chosen (C-6)."""
        return await self._http.model(
            OverlapsResponse,
            "POST",
            f"{_SCREENING}/overlaps",
            body=OverlapsRequest(geometry=to_geojson(geometry), limit=limit),
        )

    async def list_runs(
        self,
        *,
        kind: RunKind | None = None,
        user_id: int | None = None,
        page: int = 1,
        size: int | None = None,
    ) -> Page[ScreeningRunItem]:
        """The pinned runs, newest first."""
        return await self._http.model(
            Page[ScreeningRunItem],
            "GET",
            f"{_SCREENING}/runs",
            query={"kind": kind, "userId": user_id, "page": page, "size": size},
        )

    async def get_run(self, run_id: int) -> ScreeningRunResponse:
        return await self._http.model(ScreeningRunResponse, "GET", f"{_SCREENING}/runs/{run_id}")


__all__ = [
    "CarOverlapItem",
    "CarOverlaps",
    "CoverageStatementResponse",
    "EsgOverlapItem",
    "FindingMeasuredAgainst",
    "NormReferenceRef",
    "OverlapsRequest",
    "OverlapsResponse",
    "Screening",
    "ScreeningCandidate",
    "ScreeningCoverage",
    "ScreeningFinding",
    "ScreeningItemRequest",
    "ScreeningOutcome",
    "ScreeningPreflightRequest",
    "ScreeningPreflightResponse",
    "ScreeningProperty",
    "ScreeningRequest",
    "ScreeningResponse",
    "ScreeningResult",
    "ScreeningRunItem",
    "ScreeningRunResponse",
]
