"""The policy layer: policies already running, and the collision check against them."""

import datetime
from collections.abc import Sequence

from agronext_gis_sdk._http import API_PREFIX, HttpClient
from agronext_gis_sdk._wire import GeoJson, Page, WireModel

_POLICIES = f"{API_PREFIX}/policies"


class PolicySeasonItem(WireModel):
    """A safra, as the overlap check reports the ones it asked.

    The API calls this schema `SeasonItem` inside its policies app; the SDK
    names it apart from the rates' `SeasonItem`, which carries more.
    """

    id: int
    label: str
    ordinal: int
    is_latest: bool
    retired_at: datetime.datetime | None = None


class PolicyPlantingWindowItem(WireModel):
    """A planting window, as the overlap check reports the ones it asked."""

    id: int
    label: str
    starts_on: datetime.date
    ends_on: datetime.date


class PolicyOverlapRequest(WireModel):
    """C-18: does this polygon collide with a running policy?

    With no `season_ids`, the safras open today are asked. `planting_window_ids`
    narrows the question to policies sold under those windows.
    """

    geometry: GeoJson
    product_id: int | None = None
    season_ids: Sequence[int] | None = None
    running_only: bool = True
    planting_window_ids: Sequence[int] | None = None


class PolicyOverlapItem(WireModel):
    policy_id: str
    area_id: int
    season_id: int
    season_label: str
    product_id: int
    product_code: str
    is_running: bool
    planting_window_id: int | None = None
    planting_window_label: str | None = None
    overlap_ha: float
    overlap_pct: float
    geometry: GeoJson


class PolicyOverlapResponse(WireModel):
    """The collisions, and the safras and windows actually asked — undated safras
    are never open, so they are listed as unchecked rather than silently skipped."""

    checked_seasons: Sequence[PolicySeasonItem]
    checked_planting_windows: Sequence[PolicyPlantingWindowItem] = ()
    unchecked_undated_seasons: Sequence[PolicySeasonItem] = ()
    total_matches: int
    matches: Sequence[PolicyOverlapItem]


class PolicyAreaItem(WireModel):
    """One policy polygon of the layer."""

    id: int
    policy_id: str
    season_id: int
    product_id: int
    is_running: bool
    area_ha: float
    load_id: int
    planting_window_id: int | None = None
    planting_window_label: str | None = None
    geometry: GeoJson | None = None


class PolicyAreaInput(WireModel):
    """One polygon of one policy, in a load."""

    policy_id: str
    geometry: GeoJson


class PolicyLoadRequest(WireModel):
    """A load: one safra, one produto, the polygons in it — APPENDED to the layer."""

    season_id: int
    product_id: int
    source_note: str | None = None
    planting_window_id: int | None = None
    areas: Sequence[PolicyAreaInput]


class PolicyLoadResponse(WireModel):
    load_id: int
    written: int
    duplicates_in_file: int
    already_present: int


class PolicyLoadItem(WireModel):
    """Provenance of one load: which spreadsheet, by whom, when."""

    id: int
    season_id: int
    season_label: str
    loaded_at: datetime.datetime
    loaded_by_username: str
    source_note: str | None = None
    row_count: int


class Policies:
    """`gis.policies` — the running policies, and the overlap check against them."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def check_overlap(self, request: PolicyOverlapRequest) -> PolicyOverlapResponse:
        """Does this polygon collide with a policy already running? Reads only."""
        return await self._http.model(
            PolicyOverlapResponse, "POST", f"{_POLICIES}/overlap", body=request
        )

    async def list_policy_areas(  # noqa: PLR0913 — the listing's filters, all keyword-only
        self,
        *,
        season_id: int | None = None,
        product_id: int | None = None,
        policy_id: str | None = None,
        running_only: bool = True,
        planting_window_id: int | None = None,
        unwindowed_only: bool = False,
        include_geometry: bool = False,
        page: int = 1,
        size: int | None = None,
    ) -> Page[PolicyAreaItem]:
        """The policy layer, newest first."""
        return await self._http.model(
            Page[PolicyAreaItem],
            "GET",
            f"{_POLICIES}/areas",
            query={
                "seasonId": season_id,
                "productId": product_id,
                "policyId": policy_id,
                "runningOnly": running_only,
                "plantingWindowId": planting_window_id,
                "unwindowedOnly": unwindowed_only,
                "includeGeometry": include_geometry,
                "page": page,
                "size": size,
            },
        )

    async def list_loads(
        self, *, season_id: int | None = None, page: int = 1, size: int | None = None
    ) -> Page[PolicyLoadItem]:
        return await self._http.model(
            Page[PolicyLoadItem],
            "GET",
            f"{_POLICIES}/loads",
            query={"seasonId": season_id, "page": page, "size": size},
        )

    async def load(self, request: PolicyLoadRequest) -> PolicyLoadResponse:
        """APPEND policies to the layer for one (safra, produto)."""
        return await self._http.model(
            PolicyLoadResponse, "POST", f"{_POLICIES}/loads", body=request
        )

    async def stand_down(self, area_id: int) -> PolicyAreaItem:
        """The policy ended: it stops running, and the row stays for reference."""
        return await self._http.model(
            PolicyAreaItem, "POST", f"{_POLICIES}/areas/{area_id}/stand-down"
        )

    async def delete_policy_area(self, area_id: int) -> None:
        """This polygon should never have been loaded: remove it."""
        await self._http.nothing("DELETE", f"{_POLICIES}/areas/{area_id}")


__all__ = [
    "Policies",
    "PolicyAreaInput",
    "PolicyAreaItem",
    "PolicyLoadItem",
    "PolicyLoadRequest",
    "PolicyLoadResponse",
    "PolicyOverlapItem",
    "PolicyOverlapRequest",
    "PolicyOverlapResponse",
    "PolicyPlantingWindowItem",
    "PolicySeasonItem",
]
