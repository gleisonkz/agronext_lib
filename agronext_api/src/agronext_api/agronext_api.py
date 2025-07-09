from dataclasses import dataclass
import inspect
from collections.abc import Iterable
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Awaitable, Callable, Optional

from fastapi import (
    FastAPI,
    APIRouter,
    status,
    Path, Query,
)
from fastapi.responses import RedirectResponse
import uvicorn

from .apps.health_check.router import router as health_check_router
from .config.settings import api_settings
from .exceptions.base import StartupError, ShutdownError
from .exceptions import init_error_handling
from .extensions import init_extensions

# from .integrations import close_integrations, init_integrations
from .logger import close_logger, get_logger, init_logger, DEBUG
from .middlewares import init_middlewares
from .security import init_security

AsyncEvent = Callable[[], Awaitable[None]]
SyncEvent = Callable[[], None]
LifecycleFn = AsyncEvent | SyncEvent


@dataclass(frozen=True)
class LifeSpanEvent:
    startup: LifecycleFn
    shutdown: LifecycleFn


def create_lifespan_event(
    startup: LifecycleFn,
    shutdown: LifecycleFn,
) -> LifeSpanEvent:
    return LifeSpanEvent(
        startup=startup,
        shutdown=shutdown,
    )


class LifespanManager:
    def __init__(self, custom_events: list[LifeSpanEvent]) -> None:
        self.custom_events = custom_events

    @asynccontextmanager
    async def __call__(self, app: FastAPI) -> AsyncGenerator:
        # fail fast
        try:
            lifespan_logger = get_logger("lifespan")

            lifespan_logger.debug("Starting startup context")
            ## Run standard startup events
            # standard_startup_events

            ## Run custom startup events
            for startup_event in (event.startup for event in self.custom_events):
                await startup_event() if inspect.iscoroutinefunction(
                    startup_event
                ) else startup_event()
            lifespan_logger.debug("Exiting startup context")

        except Exception as e:
            lifespan_logger.error(f"Error during startup: {e}")
            raise StartupError(f"Error during startup: {e}")

        yield

        lifespan_logger.debug("Starting shutdown context")
        shutdown_errors = []

        ## Run custom shutdown events
        for shutdown_event in (event.shutdown for event in self.custom_events):
            try:
                if inspect.iscoroutinefunction(shutdown_event):
                    await shutdown_event()
                else:
                    shutdown_event()

            except Exception as e:
                lifespan_logger.error(f"Error during custom shutdown: {e}")
                shutdown_errors.append(e)

        ## Run standard shutdown events
        ## Fail Safely
        for fn in ():  # standard_shutdown_events:
            try:
                await fn() if inspect.iscoroutinefunction(fn) else fn()
            except Exception as e:
                lifespan_logger.error(
                    f"Error during standard shutdown ({fn.__name__}): {e}"
                )
                shutdown_errors.append(e)
        lifespan_logger.debug("Exiting shutdown context")
        close_logger()

        if shutdown_errors:
            raise ShutdownError(
                f"One or more shutdown events failed: {shutdown_errors}"
            )


def create_router(
    prefix: str = "", tags: Optional[list[str]] = None, **kwargs
) -> APIRouter:
    """
    Creates a new APIRouter instance.

    :param prefix: A string to be added to all route paths in the router.
    :param tags: A list of strings for tagging routes.
    :return: An APIRouter instance.
    """
    _prefix = prefix if prefix.startswith("/") else f"/{prefix}"
    router = APIRouter(prefix=_prefix, tags=tags, **kwargs)

    return router


def create_api(
    *,
    apps: Iterable[APIRouter],
    title: str = "Agronext Backend API",
    version: str | None = None,
    description: str = "Backend for Agronext Platform",
    custom_lifespan_events: Optional[Iterable[tuple[LifecycleFn, LifecycleFn]]] = None,
    custom_errors: Optional[dict[str, tuple[int, str]]] = None,
    custom_exception_handlers: Optional[dict[str, tuple[int, str]]] = None,
    custom_middlewares: Optional[list[tuple[str, str]]] = None,
) -> FastAPI:
    log_level = DEBUG if api_settings.DEBUG else api_settings.LOG_LEVEL
    init_logger(log_level)
    lifespan_events = (
        [create_lifespan_event(*event) for event in custom_lifespan_events]
        if custom_lifespan_events
        else []
    )
    app = FastAPI(
        title=title,
        description=description,
        version=version,
        lifespan=LifespanManager(lifespan_events),
    )

    init_error_handling(app, custom_exception_handlers or [])
    init_security(app)
    init_middlewares(app, custom_middlewares or [])
    init_extensions(app, custom_errors or [])

    @app.get(("/"), status_code=status.HTTP_200_OK, include_in_schema=False)
    async def home():
        """
        Home endpoint for the API.
        """
        return RedirectResponse(url="/health_check/")

    app.include_router(health_check_router)

    for router in apps:
        app.include_router(router)

    return app


def run(
    api: FastAPI,
    host: str,
    port: int,
    factory: bool,
) -> None:
    uvicorn.run(
        api,
        host=host,
        port=port,
        factory=factory,
    )
