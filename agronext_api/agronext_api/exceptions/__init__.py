import traceback
from datetime import datetime

from agronext_database.exceptions import (
    QueryError,
    ResourceAlreadyExists,
    ResourceNotFound,
)
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse

from ..logger import get_logger
from .http import BadRequest, Conflict, Forbidden, Unauthorized


def __user_friendly_json(status_code: int, error: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": error, "user_friendly": True})


error_logger = get_logger("errors")


def init_error_handling(app: FastAPI) -> None:
    @app.exception_handler(BadRequest)
    async def bad_request_exception_handler(request: Request, exc: BadRequest) -> JSONResponse:
        return __user_friendly_json(status.HTTP_400_BAD_REQUEST, str(exc))

    @app.exception_handler(Unauthorized)
    async def unauthorized_exception_handler(request: Request, exc: Unauthorized) -> JSONResponse:
        return __user_friendly_json(status.HTTP_401_UNAUTHORIZED, str(exc))

    @app.exception_handler(Forbidden)
    async def forbidden_exception_handler(request: Request, exc: Forbidden) -> JSONResponse:
        return __user_friendly_json(status.HTTP_403_FORBIDDEN, str(exc))

    @app.exception_handler(Conflict)
    async def conflict_exception_handler(request: Request, exc: Conflict) -> JSONResponse:
        return __user_friendly_json(status.HTTP_409_CONFLICT, str(exc))

    @app.exception_handler(ResourceNotFound)
    async def resource_not_found_exception_handler(request: Request, exc: ResourceNotFound) -> JSONResponse:
        return __user_friendly_json(status.HTTP_404_NOT_FOUND, str(exc))

    @app.exception_handler(ResourceAlreadyExists)
    async def resource_already_exists_exception_handler(request: Request, exc: ResourceAlreadyExists) -> JSONResponse:
        return __user_friendly_json(status.HTTP_409_CONFLICT, str(exc))

    @app.exception_handler(Exception)
    async def custom_http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
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
            detail=f"Internal Server Error: {type(exc).__name__}",
        )
        return await http_exception_handler(request, exception)
