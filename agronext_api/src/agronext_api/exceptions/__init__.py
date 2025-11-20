import traceback
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse

from ..logger import get_logger
from .http import BadRequest, Conflict, Forbidden, Unauthorized

error_logger = get_logger("errors")


def __user_friendly_json(status_code: int, error: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code, content={"error": error, "user_friendly": True}
    )


"""
    If any of the errors below is raised it is captured by the exception handler
    and a JSON response is returned with the error message and a user friendly message
    The error message is logged in the error logger
"""


def init_error_handling(app: FastAPI, custom_handlers: list) -> None:
    @app.exception_handler(BadRequest)
    async def bad_request_exception_handler(
        request: Request, exc: BadRequest
    ) -> JSONResponse:
        return __user_friendly_json(exc.status_code, str(exc))

    @app.exception_handler(Unauthorized)
    async def unauthorized_exception_handler(
        request: Request, exc: Unauthorized
    ) -> JSONResponse:
        return __user_friendly_json(exc.status_code, str(exc))

    @app.exception_handler(Forbidden)
    async def forbidden_exception_handler(
        request: Request, exc: Forbidden
    ) -> JSONResponse:
        return __user_friendly_json(exc.status_code, str(exc))

    @app.exception_handler(Conflict)
    async def conflict_exception_handler(
        request: Request, exc: Conflict
    ) -> JSONResponse:
        return __user_friendly_json(exc.status_code, str(exc))

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

        return await http_exception_handler(request, exception)

    for handler in custom_handlers:
        raise NotImplementedError(
            f"Custom error handler {handler} is not implemented. Please implement it."
        )
