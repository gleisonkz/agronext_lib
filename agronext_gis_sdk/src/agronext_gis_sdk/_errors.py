"""The SDK's own error hierarchy: nothing from httpx or pydantic escapes raw.

Every failure a caller can see is an `AgronextGisError`:

- `ApiError` — the API answered with an error. Built from its RFC 9457 problem
  body, so `code` is the API's machine code (`rates.copy.windows_undeclared`),
  `correlation_id` is the one in the API's own logs, and `context` carries the
  rejection's fields (`undeclared_product_ids`, …). One subclass per status a
  caller branches on; any other status is a plain `ApiError`.
- `PolygonsRefusedError` — the one refusal typed beyond its status: the rate of
  a sale was asked and at least one polygon cannot be resolved. A sale system
  has to tell its buyer WHICH polygon and WHY, so `refusals` holds that per
  polygon instead of leaving it to be dug out of `context`.
- `TransportError` — no answer at all: the connection failed or timed out.
- `ResponseMismatchError` — an answer this SDK version cannot read.

The cause is always chained (`raise … from`), and nothing here logs: the caller
decides what an error is worth, and logs it once, where it handles it.
"""

import dataclasses
import enum
import http
from collections.abc import Mapping, Sequence
from typing import Any, Final

#: The problem-details members that are not part of a rejection's context.
_PROBLEM_MEMBERS: Final[frozenset[str]] = frozenset(
    {"type", "title", "status", "detail", "code", "correlationId", "errors"}
)


class AgronextGisError(Exception):
    """Anything that went wrong talking to the agronext_gis API."""


class TransportError(AgronextGisError):
    """The request got no answer: connection refused, reset, or timed out."""

    def __init__(self, message: str, *, method: str, url: str) -> None:
        super().__init__(message)
        self.method = method
        self.url = url


class ResponseMismatchError(AgronextGisError):
    """The API answered, and the answer does not fit this SDK's model of it."""

    def __init__(self, message: str, *, method: str, url: str, status: int) -> None:
        super().__init__(message)
        self.method = method
        self.url = url
        self.status = status


class ApiError(AgronextGisError):
    """The API refused or failed the request, and said why."""

    def __init__(  # noqa: PLR0913 — one problem body is this many facts, keyword-only
        self,
        detail: str,
        *,
        status: int,
        code: str | None,
        correlation_id: str | None,
        errors: Sequence[Mapping[str, Any]] = (),
        context: Mapping[str, Any] | None = None,
        method: str,
        url: str,
    ) -> None:
        super().__init__(f"{status} {code or _phrase(status)}: {detail}")
        self.detail = detail
        self.status = status
        #: The API's machine code, stable across wording changes — branch on this.
        self.code = code
        #: The same id the API logged the request under.
        self.correlation_id = correlation_id
        #: Per-field issues of a validation failure (422 with `request.invalid`).
        self.errors = errors
        #: The rejection's own fields, as the API named them.
        self.context: Mapping[str, Any] = context or {}
        self.method = method
        self.url = url


class UnauthorizedError(ApiError):
    """401: no key, or a key the API does not know."""


class ForbiddenError(ApiError):
    """403: the key's user may not do this (a read-only user writing, say)."""


class NotFoundError(ApiError):
    """404: the path, or an id in it, names nothing."""


class ConflictError(ApiError):
    """409: the request clashes with the current state (retired, taken, in use)."""


class UnprocessableError(ApiError):
    """422: the request is malformed, or a rule of the API refuses it."""


class ServerError(ApiError):
    """5xx: the API failed. `correlation_id` is what to quote when reporting it."""


class RateRefusalCode(enum.StrEnum):
    """Why the API refuses to resolve the rate of one polygon — what
    `PolygonRefusal.code` holds, and `ApiError.code` when one polygon is asked.

    The API's own codes. One it adds later still arrives, as its plain string:
    `PolygonRefusal.code` is a `str`, and these members compare equal to it.
    """

    #: Part of the polygon lies where the produto may not be sold.
    FORBIDDEN_AREA = "rates.resolve.forbidden_area"
    #: Part of the polygon has no rate at any level.
    UNPRICED_AREA = "rates.resolve.unpriced_area"
    #: No rate at all covers the polygon.
    NO_RATES = "rates.resolve.no_rates_for_cell"
    #: The polygon is too large for the grid — for every grid, when none was named.
    TILE_BUDGET_EXCEEDED = "rates.resolve.tile_budget_exceeded"


@dataclasses.dataclass(frozen=True, slots=True)
class PolygonRefusal:
    """Why ONE polygon of a sale could not be resolved."""

    #: Its position among the polygons given.
    polygon_index: int
    #: The API's machine code for the reason — compare with `RateRefusalCode`.
    code: str
    #: The reason in words, as the API states it.
    detail: str
    #: The reason's own fields: how much of the polygon (`forbidden_area_pct`,
    #: `unresolved_area_pct`), which áreas forbid it (`forbidding_areas`), and
    #: where on the grid (`grid`, `forbidden_cells`, `unresolved_cells`).
    context: Mapping[str, Any]


class PolygonsRefusedError(UnprocessableError):
    """422 `rates.resolve.polygons_refused`: at least one polygon of the sale
    cannot be resolved, so NONE was — and no run was pinned.

    `refusals` names every polygon that failed, in the order given; the API
    tries them all before refusing, so this one error says everything that has
    to change.
    """

    def __init__(  # noqa: PLR0913 — one problem body is this many facts, keyword-only
        self,
        detail: str,
        *,
        status: int,
        code: str | None,
        correlation_id: str | None,
        refusals: Sequence[PolygonRefusal],
        errors: Sequence[Mapping[str, Any]] = (),
        context: Mapping[str, Any] | None = None,
        method: str,
        url: str,
    ) -> None:
        super().__init__(
            detail,
            status=status,
            code=code,
            correlation_id=correlation_id,
            errors=errors,
            context=context,
            method=method,
            url=url,
        )
        self.refusals: Sequence[PolygonRefusal] = tuple(refusals)


#: The code of the refusal `PolygonsRefusedError` types, and where its body
#: lists the polygons.
POLYGONS_REFUSED_CODE: Final[str] = "rates.resolve.polygons_refused"
_REFUSED_MEMBER: Final[str] = "refused"


_BY_STATUS: Final[Mapping[int, type[ApiError]]] = {
    http.HTTPStatus.UNAUTHORIZED: UnauthorizedError,
    http.HTTPStatus.FORBIDDEN: ForbiddenError,
    http.HTTPStatus.NOT_FOUND: NotFoundError,
    http.HTTPStatus.CONFLICT: ConflictError,
    http.HTTPStatus.UNPROCESSABLE_ENTITY: UnprocessableError,
}


def api_error(status: int, body: object, *, method: str, url: str) -> ApiError:
    """The typed error for an error response, from its problem body when it has one."""
    problem: Mapping[str, Any] = body if isinstance(body, Mapping) else {}
    error_type = (
        ServerError
        if status >= http.HTTPStatus.INTERNAL_SERVER_ERROR
        else _BY_STATUS.get(status, ApiError)
    )
    detail = problem.get("detail")
    errors = problem.get("errors")
    code = _text(problem.get("code"))
    context = {key: value for key, value in problem.items() if key not in _PROBLEM_MEMBERS}
    refusals = _refusals(context) if code == POLYGONS_REFUSED_CODE else None
    if refusals is not None and error_type is UnprocessableError:
        return PolygonsRefusedError(
            detail if isinstance(detail, str) else _phrase(status),
            status=status,
            code=code,
            correlation_id=_text(problem.get("correlationId")),
            refusals=refusals,
            errors=errors if isinstance(errors, list) else (),
            context=context,
            method=method,
            url=url,
        )
    return error_type(
        detail if isinstance(detail, str) else _phrase(status),
        status=status,
        code=code,
        correlation_id=_text(problem.get("correlationId")),
        errors=errors if isinstance(errors, list) else (),
        context=context,
        method=method,
        url=url,
    )


def _refusals(context: Mapping[str, Any]) -> tuple[PolygonRefusal, ...] | None:
    """The refused polygons of a problem body — or None when it lists them in
    a shape this SDK does not know.

    None and not a guess: the error is then typed by its status alone, with the
    body untouched in `context`, as any refusal this version cannot read is.
    """
    listed = context.get(_REFUSED_MEMBER)
    if not isinstance(listed, list) or not listed:
        return None
    refusals: list[PolygonRefusal] = []
    for entry in listed:
        refusal = _refusal(entry)
        if refusal is None:
            return None
        refusals.append(refusal)
    return tuple(refusals)


def _refusal(entry: object) -> PolygonRefusal | None:
    if not isinstance(entry, Mapping):
        return None
    index, code = entry.get("polygon_index"), entry.get("code")
    detail, context = entry.get("detail"), entry.get("context")
    # `type(...) is int`: a JSON `true` is an `int` to `isinstance`.
    if type(index) is not int or not isinstance(code, str) or not isinstance(detail, str):
        return None
    if not isinstance(context, Mapping):
        return None
    return PolygonRefusal(polygon_index=index, code=code, detail=detail, context=dict(context))


#: Every reason phrase HTTP names, by status.
_PHRASES: Final[Mapping[int, str]] = {status.value: status.phrase for status in http.HTTPStatus}


def _phrase(status: int) -> str:
    """The reason phrase — or the bare number for a status HTTP never named."""
    return _PHRASES.get(status, str(status))


def _text(value: object) -> str | None:
    return value if isinstance(value, str) else None


__all__ = [
    "POLYGONS_REFUSED_CODE",
    "AgronextGisError",
    "ApiError",
    "ConflictError",
    "ForbiddenError",
    "NotFoundError",
    "PolygonRefusal",
    "PolygonsRefusedError",
    "RateRefusalCode",
    "ResponseMismatchError",
    "ServerError",
    "TransportError",
    "UnauthorizedError",
    "UnprocessableError",
    "api_error",
]
