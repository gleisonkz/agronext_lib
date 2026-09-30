"""The one place that speaks HTTP: httpx, wrapped once (§13.2.1).

Revised from plug_sdk's `BaseAsyncClient`, which subclassed `httpx.AsyncClient`
(so every httpx method leaked into the SDK's surface), returned `Response | T`,
logged at ERROR and re-raised httpx's own errors. Here:

- httpx is COMPOSED, never inherited: callers see the SDK's methods only.
- Every call returns the typed model, or raises one of `_errors`.
- TLS verification is always on. A private CA is a bundle PATH (§22.5); there
  is no switch to turn verification off.
- The timeout is set once, at construction (§23.4): no call can be made
  without one.
- Retries cover CONNECTION failures only — the request never reached the API,
  so retrying it cannot write twice. A timeout or an error answer is never
  retried.
- Nothing logs above DEBUG: the caller decides what a failure is worth.
"""

import logging
import os
import ssl
import time
from collections.abc import Callable, Mapping, Sequence
from datetime import date, datetime
from enum import Enum
from functools import cache
from typing import Final

import httpx
from pydantic import TypeAdapter, ValidationError

from agronext_gis_sdk._errors import ResponseMismatchError, TransportError, api_error
from agronext_gis_sdk._wire import WireModel

logger = logging.getLogger("agronext_gis_sdk")

#: Where every capability lives under the base URL.
API_PREFIX: Final[str] = "/api/v1"
#: How a caller authenticates: its API key.
API_KEY_HEADER: Final[str] = "X-API-Key"
#: The header the API reads a caller's correlation id from (§20.1) — unless the
#: deployment renamed it (`API_CORRELATION_ID_HEADER`), which is why the client
#: takes the name as a setting.
REQUEST_ID_HEADER: Final[str] = "X-Request-ID"
#: Seconds for connect, read, write and pool alike, unless the caller says otherwise.
DEFAULT_TIMEOUT_S: Final[float] = 30.0
#: How many times a connection that could not be ESTABLISHED is retried.
DEFAULT_CONNECT_RETRIES: Final[int] = 2
#: Milliseconds per second, for the DEBUG line's duration.
_MS: Final[int] = 1000

#: A query parameter's value, before it is written into the URL.
type QueryValue = str | int | float | bool | date | datetime | Enum | Sequence[int | str] | None


class HttpClient:
    """Authenticated, typed requests to one agronext_gis API."""

    def __init__(  # noqa: PLR0913 — the connection's settings, all keyword-only
        self,
        *,
        base_url: str,
        api_key: str,
        timeout: float,
        ca_bundle: str | os.PathLike[str] | None,
        connect_retries: int,
        request_id: Callable[[], str | None] | None,
        request_id_header: str,
        transport: httpx.AsyncBaseTransport | None,
    ) -> None:
        verify: ssl.SSLContext | bool = (
            ssl.create_default_context(cafile=os.fspath(ca_bundle))
            if ca_bundle is not None
            else True
        )
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={API_KEY_HEADER: api_key, "Accept": "application/json"},
            timeout=httpx.Timeout(timeout),
            transport=transport or httpx.AsyncHTTPTransport(verify=verify, retries=connect_retries),
            follow_redirects=False,
        )
        self._request_id = request_id
        self._request_id_header = request_id_header

    async def aclose(self) -> None:
        await self._client.aclose()

    async def model[M: WireModel](  # noqa: PLR0913 — one request's parts, keyword-only
        self,
        model: type[M],
        method: str,
        path: str,
        *,
        query: Mapping[str, QueryValue] | None = None,
        body: WireModel | None = None,
        files: Mapping[str, tuple[str, bytes, str]] | None = None,
    ) -> M:
        """One request whose answer is one `model`."""
        response = await self._send(method, path, query=query, body=body, files=files)
        return _parse(TypeAdapter(model), response)

    async def models[M: WireModel](
        self,
        model: type[M],
        method: str,
        path: str,
        *,
        query: Mapping[str, QueryValue] | None = None,
        body: WireModel | None = None,
    ) -> list[M]:
        """One request whose answer is a JSON array of `model`."""
        response = await self._send(method, path, query=query, body=body)
        return _parse(_list_adapter(model), response)

    async def nothing(self, method: str, path: str, *, body: WireModel | None = None) -> None:
        """One request whose answer carries no body the caller needs."""
        await self._send(method, path, body=body)

    async def content(self, method: str, path: str, *, body: WireModel | None = None) -> bytes:
        """One request whose answer is a file."""
        return (await self._send(method, path, body=body)).content

    async def _send(
        self,
        method: str,
        path: str,
        *,
        query: Mapping[str, QueryValue] | None = None,
        body: WireModel | None = None,
        files: Mapping[str, tuple[str, bytes, str]] | None = None,
    ) -> httpx.Response:
        headers: dict[str, str] = {}
        request_id = self._request_id() if self._request_id is not None else None
        if request_id:
            headers[self._request_id_header] = request_id
        started = time.perf_counter()
        try:
            response = await self._client.request(
                method,
                path,
                params=_query(query or {}),
                # Only what the caller SET: an unset field is left to the API's
                # own default, so the two can never disagree about one.
                json=(
                    body.model_dump(mode="json", by_alias=True, exclude_unset=True)
                    if body is not None
                    else None
                ),
                files=files,
                headers=headers,
            )
        except httpx.TimeoutException as timed_out:
            msg = f"{method} {path}: no answer within the timeout"
            raise TransportError(msg, method=method, url=path) from timed_out
        except httpx.TransportError as unreachable:
            msg = f"{method} {path}: {unreachable}"
            raise TransportError(msg, method=method, url=path) from unreachable
        logger.debug(
            "agronext_gis %s %s -> %s in %.0f ms",
            method,
            path,
            response.status_code,
            (time.perf_counter() - started) * _MS,
            extra={"request_id": response.headers.get(self._request_id_header)},
        )
        if response.is_error:
            raise api_error(
                response.status_code,
                _problem_body(response),
                method=method,
                url=str(response.url),
            )
        return response


def _parse[T](adapter: TypeAdapter[T], response: httpx.Response) -> T:
    try:
        return adapter.validate_json(response.content)
    except ValidationError as mismatch:
        msg = f"{response.request.method} {response.url}: the answer does not fit {adapter}"
        raise ResponseMismatchError(
            msg,
            method=response.request.method,
            url=str(response.url),
            status=response.status_code,
        ) from mismatch


@cache
def _list_adapter[M: WireModel](model: type[M]) -> TypeAdapter[list[M]]:
    return TypeAdapter(list[model])  # type: ignore[valid-type]  # a runtime-built alias


def _problem_body(response: httpx.Response) -> object:
    """An error answer's body, when it declares JSON — the API's problem details.

    A body that is not JSON (a proxy's HTML page) is no problem body at all, and
    the error is typed by its status alone. One that CLAIMS JSON and does not
    parse is an answer this SDK cannot read, and says so (§23.3).
    """
    if "json" not in response.headers.get("content-type", ""):
        return None
    try:
        body: object = response.json()
    except ValueError as unreadable:
        msg = f"{response.request.method} {response.url}: an unreadable JSON error body"
        raise ResponseMismatchError(
            msg,
            method=response.request.method,
            url=str(response.url),
            status=response.status_code,
        ) from unreadable
    return body


#: One query parameter as httpx takes it.
type _QueryPair = tuple[str, str | int | float | bool | None]


def _query(values: Mapping[str, QueryValue]) -> list[_QueryPair]:
    """Query parameters as the API reads them: absent when None, lists repeated."""
    pairs: list[_QueryPair] = []
    for name, value in values.items():
        if value is None:
            continue
        if isinstance(value, Sequence) and not isinstance(value, str):
            pairs.extend((name, _text(item)) for item in value)
        else:
            pairs.append((name, _text(value)))
    return pairs


def _text(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, date | datetime):
        return value.isoformat()
    return str(value)


__all__ = [
    "API_KEY_HEADER",
    "API_PREFIX",
    "DEFAULT_CONNECT_RETRIES",
    "DEFAULT_TIMEOUT_S",
    "REQUEST_ID_HEADER",
    "HttpClient",
    "QueryValue",
]
