"""The entry point: one client, one namespace per area of the API."""

import enum
import os
from collections.abc import AsyncIterator, Awaitable, Callable, Mapping
from types import TracebackType
from typing import Any, Self

import httpx

from agronext_gis_sdk._access import Access
from agronext_gis_sdk._areas import Areas, Regions
from agronext_gis_sdk._geography import Geography
from agronext_gis_sdk._groups import Groups
from agronext_gis_sdk._http import (
    DEFAULT_CONNECT_RETRIES,
    DEFAULT_TIMEOUT_S,
    REQUEST_ID_HEADER,
    HttpClient,
)
from agronext_gis_sdk._policies import Policies
from agronext_gis_sdk._rates import Pairs, Products, Rates, Seasons
from agronext_gis_sdk._screening import Screening
from agronext_gis_sdk._tools import Tools
from agronext_gis_sdk._wire import Page, WireModel

#: Where the readiness probe lives: beside the API, not under its prefix.
_READINESS_PATH = "/health/ready"


class ProbeStatus(enum.StrEnum):
    UP = "up"
    DOWN = "down"


class ReadinessResponse(WireModel):
    """Whether the API can serve, and which dependency is down when it cannot."""

    status: ProbeStatus
    checks: Mapping[str, ProbeStatus]


class AgronextGisClient:
    """An async client for the agronext_gis API.

    ```python
    async with AgronextGisClient(base_url="https://gis.example", api_key=key) as gis:
        answer = await gis.rates.resolve(polygon, product_id=8, deductible_id=2, cell_m=100)
    ```

    `base_url` is the API's root (the `/api/v1` prefix is the client's to add).
    `api_key` is a key the API minted for a user; what it may do is that user's
    `can_write`. `timeout` bounds every request. `ca_bundle` points at a private
    CA's certificates; TLS is verified either way. `connect_retries` retries a
    connection that could not be established — never a request that got an
    answer. `request_id`, when given, is called per request and its value sent
    in `request_id_header` — `X-Request-ID` unless the deployment renamed it
    (`API_CORRELATION_ID_HEADER`). When it is a UUID the API ADOPTS it: the
    request is logged, recorded and answered (`ApiError.correlation_id`) under
    the caller's id. Any other value is logged beside a fresh id the API mints.
    `transport` replaces the network — a test's `httpx.MockTransport`, or
    `httpx.ASGITransport` to run against an API in the same process.
    """

    def __init__(  # noqa: PLR0913 — the connection's settings, all keyword-only
        self,
        *,
        base_url: str,
        api_key: str,
        timeout: float = DEFAULT_TIMEOUT_S,
        ca_bundle: str | os.PathLike[str] | None = None,
        connect_retries: int = DEFAULT_CONNECT_RETRIES,
        request_id: Callable[[], str | None] | None = None,
        request_id_header: str = REQUEST_ID_HEADER,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._http = HttpClient(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            ca_bundle=ca_bundle,
            connect_retries=connect_retries,
            request_id=request_id,
            request_id_header=request_id_header,
            transport=transport,
        )
        #: The caller, and user administration.
        self.access = Access(self._http)
        #: Country, UFs, municípios; where a geometry falls.
        self.geography = Geography(self._http)
        #: CAR imóveis and what the registries say about them.
        self.screening = Screening(self._http)
        #: The catálogo of áreas.
        self.areas = Areas(self._http)
        #: Named sets of áreas.
        self.regions = Regions(self._http)
        #: Produtos and their franquias.
        self.products = Products(self._http)
        #: Safras, their produtos, and copying between safras.
        self.seasons = Seasons(self._http)
        #: One (safra, produto): abrangência, fatores, windows, adjustments, contests.
        self.pairs = Pairs(self._http)
        #: The rates, their trail, and resolving them over a polygon.
        self.rates = Rates(self._http)
        #: The running policies, and the overlap check against them.
        self.policies = Policies(self._http)
        #: The distance check between a policy's polygons.
        self.groups = Groups(self._http)
        #: KML in and out, polygon measurement.
        self.tools = Tools(self._http)

    async def ready(self) -> ReadinessResponse:
        """Whether the API can serve. A down dependency answers 503, which raises
        `ServerError` — its `context` names the dependency."""
        return await self._http.model(ReadinessResponse, "GET", _READINESS_PATH)

    async def aclose(self) -> None:
        """Close the connection pool. `async with` does it for you."""
        await self._http.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()


async def paginate[T: WireModel](
    fetch: Callable[..., Awaitable[Page[T]]], /, **filters: Any
) -> AsyncIterator[T]:
    """Every item of a paged listing, page after page.

    ```python
    async for area in paginate(gis.areas.list_areas, level=LayerLevel.STATE):
        ...
    ```

    `filters` are the listing's own keyword arguments; `page` is this helper's.
    """
    page = 1
    while True:
        answer = await fetch(**filters, page=page)
        for item in answer.items:
            yield item
        if page >= answer.pages:
            return
        page += 1


__all__ = ["AgronextGisClient", "ProbeStatus", "ReadinessResponse", "paginate"]
