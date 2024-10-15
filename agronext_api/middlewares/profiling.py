import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..logger import get_logger

middleware_logger = get_logger("middlewares")


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter_ns()
        response = await call_next(request)
        process_time = time.perf_counter_ns() - start_time
        process_time_ms = process_time / 1000000
        process_time_ms = round(process_time_ms, 2)
        response.headers["X-Process-Time"] = str(process_time_ms)
        middleware_logger.info(
            f"Request {request.method} {request.url._url[:-1]}{request.url.path} from {request.client.host} took {process_time_ms} milliseconds",
            extra={"request": request.url.path},
        )
        return response


