import traceback
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTasks

from ..integrations.teams import send_teams
from ..logger import get_logger
from . import http

error_logger = get_logger("errors")

_CUSTOM_ERROR_HANDLERS = frozenset({"teams"})


def __user_friendly_json(
    status_code: int,
    error: str,
    background: BackgroundTasks | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": error, "user_friendly": True},
        background=background,
    )


def __teams_background(
    request: Request, status_code: int, detail: str
) -> BackgroundTasks:
    background = BackgroundTasks()
    msg = f"Erro {status_code} — {request.method} {request.url.path}\n{detail}"
    background.add_task(send_teams, msg)
    return background


"""
    If any of the errors below is raised it is captured by the exception handler
    and a JSON response is returned with the error message and a user friendly message
    The error message is logged in the error logger
"""


def init_error_handling(app: FastAPI, custom_handlers: list[str]) -> None:
    notify_teams = False
    for handler in custom_handlers:
        if handler not in _CUSTOM_ERROR_HANDLERS:
            raise NotImplementedError(
                f"Custom error handler {handler} is not implemented. Please implement it."
            )
        if handler == "teams":
            notify_teams = True

    @app.exception_handler(http.BadRequest)
    async def bad_request_exception_handler(
        request: Request, exc: http.BadRequest
    ) -> JSONResponse:
        return __user_friendly_json(exc.status_code, str(exc))

    @app.exception_handler(http.Unauthorized)
    async def unauthorized_exception_handler(
        request: Request, exc: http.Unauthorized
    ) -> JSONResponse:
        return __user_friendly_json(exc.status_code, str(exc))

    @app.exception_handler(http.Forbidden)
    async def forbidden_exception_handler(
        request: Request, exc: http.Forbidden
    ) -> JSONResponse:
        return __user_friendly_json(exc.status_code, str(exc))

    @app.exception_handler(http.NotFound)
    async def not_found_exception_handler(
        request: Request, exc: http.NotFound
    ) -> JSONResponse:
        return __user_friendly_json(exc.status_code, str(exc))

    @app.exception_handler(http.Conflict)
    async def conflict_exception_handler(
        request: Request, exc: http.Conflict
    ) -> JSONResponse:
        return __user_friendly_json(exc.status_code, str(exc))

    @app.exception_handler(http.Locked)
    async def locked_exception_handler(
        request: Request, exc: http.Locked
    ) -> JSONResponse:
        return __user_friendly_json(exc.status_code, str(exc))

    @app.exception_handler(http.TooManyRequests)
    async def too_many_requests_exception_handler(
        request: Request, exc: http.TooManyRequests
    ) -> JSONResponse:
        return __user_friendly_json(exc.status_code, str(exc))

    @app.exception_handler(http.InternalServerError)
    async def internal_server_error_exception_handler(
        request: Request, exc: http.InternalServerError
    ) -> JSONResponse:
        background = (
            __teams_background(request, exc.status_code, str(exc))
            if notify_teams
            else None
        )
        return __user_friendly_json(exc.status_code, str(exc), background=background)

    @app.exception_handler(http.ServiceUnavailable)
    async def service_unavailable_exception_handler(
        request: Request, exc: http.ServiceUnavailable
    ) -> JSONResponse:
        background = (
            __teams_background(request, exc.status_code, str(exc))
            if notify_teams
            else None
        )
        return __user_friendly_json(exc.status_code, str(exc), background=background)

    @app.exception_handler(http.GatewayTimeout)
    async def gateway_timeout_exception_handler(
        request: Request, exc: http.GatewayTimeout
    ) -> JSONResponse:
        background = (
            __teams_background(request, exc.status_code, str(exc))
            if notify_teams
            else None
        )
        return __user_friendly_json(exc.status_code, str(exc), background=background)

    @app.exception_handler(HTTPException)
    async def http_exception_teams_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        response = await http_exception_handler(request, exc)
        if notify_teams and exc.status_code >= 500:
            response.background = __teams_background(
                request, exc.status_code, str(exc.detail)
            )
        return response

    @app.exception_handler(Exception)
    async def custom_http_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        error_details = {
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "method": request.method,
            "url": request.url._url,
            "headers": dict(request.headers),
            "client": request.client.host,
            "traceback": traceback.format_exc(),
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
        }
        error_logger.error(error_details)

        exception = HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error - {type(exc).__name__}: {str(exc)}",
        )
        response = await http_exception_handler(request, exception)
        if notify_teams:
            response.background = __teams_background(
                request,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"{type(exc).__name__}: {exc}",
            )
        return response
