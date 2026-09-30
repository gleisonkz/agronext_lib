"""The SDK's own error hierarchy: nothing from httpx or pydantic escapes raw.

Every failure a caller can see is an `AgronextGisError`:

- `ApiError` — the API answered with an error. Built from its RFC 9457 problem
  body, so `code` is the API's machine code (`rates.copy.windows_undeclared`),
  `correlation_id` is the one in the API's own logs, and `context` carries the
  rejection's fields (`undeclared_product_ids`, …). One subclass per status a
  caller branches on; any other status is a plain `ApiError`.
- `TransportError` — no answer at all: the connection failed or timed out.
- `ResponseMismatchError` — an answer this SDK version cannot read.

The cause is always chained (`raise … from`), and nothing here logs: the caller
decides what an error is worth, and logs it once, where it handles it.
"""

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
    return error_type(
        detail if isinstance(detail, str) else _phrase(status),
        status=status,
        code=_text(problem.get("code")),
        correlation_id=_text(problem.get("correlationId")),
        errors=errors if isinstance(errors, list) else (),
        context={key: value for key, value in problem.items() if key not in _PROBLEM_MEMBERS},
        method=method,
        url=url,
    )


#: Every reason phrase HTTP names, by status.
_PHRASES: Final[Mapping[int, str]] = {status.value: status.phrase for status in http.HTTPStatus}


def _phrase(status: int) -> str:
    """The reason phrase — or the bare number for a status HTTP never named."""
    return _PHRASES.get(status, str(status))


def _text(value: object) -> str | None:
    return value if isinstance(value, str) else None


__all__ = [
    "AgronextGisError",
    "ApiError",
    "ConflictError",
    "ForbiddenError",
    "NotFoundError",
    "ResponseMismatchError",
    "ServerError",
    "TransportError",
    "UnauthorizedError",
    "UnprocessableError",
    "api_error",
]
