from contextlib import asynccontextmanager, AsyncExitStack
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, APIRouter, BackgroundTasks, Response, status, Query  # noqa

from .config.settings import api_settings

# from .database import close_db, init_db
from .exceptions import init_error_handling
from .extensions import init_extensions

# from .integrations import close_integrations, init_integrations
from .logger import close_logger, get_logger, init_logger
from .middlewares import init_middlewares
from .security import init_security
from .apps.health_check.router import router as health_check_router


class AgronextAPI:
    def __init__(
        self,
        title="Agronext Backend API",
        description="Backend for Agronext Platform",
        version=api_settings.API_VERSION,
        **kwargs,
    ) -> None:
        """
        Initializes the FastAPI Wrapper with optional FastAPI arguments.
        """
        log_level = "DEBUG" if api_settings.DEBUG else api_settings.LOG_LEVEL
        init_logger(log_level)

        app = FastAPI(
            title=title,
            description=description,
            version=version,
            lifespan=self.__lifespan,
            **kwargs,
        )

        init_error_handling(app)
        init_security(app)
        init_extensions(app)
        init_middlewares(app)

        app.include_router(health_check_router)

        self._app = app
        self._routers: list[APIRouter] = []
        self._additional_lifespan_funcs: list[callable] = []
        self._wrap_lifespan()

    @asynccontextmanager
    async def __lifespan(self, app: FastAPI) -> AsyncGenerator:
        lifespan_logger = get_logger("lifespan")

        # try:
        #     await init_db()
        #     lifespan_logger.info("Database ORM initialized")
        # except BaseException as e:
        #     lifespan_logger.error(f"Error initializing database: {type(e).__name__}")
        #     raise e

        # await init_integrations()

        yield

        # close_integrations()
        # lifespan_logger.info("Integrations closed")

        # await close_db()
        # lifespan_logger.info("Database ORM closed")

        close_logger()

    def add_lifespan(self, lifespan_func: callable):
        """
        Adds an additional lifespan function that extends the existing one.

        :param lifespan_func: An async generator function that yields control back to FastAPI.
        """
        self._additional_lifespan_funcs.append(lifespan_func)
        self._wrap_lifespan()

    def _wrap_lifespan(self):
        existing_lifespan = self._app.router.lifespan_context

        @asynccontextmanager
        async def combined_lifespan(app: FastAPI):
            async with AsyncExitStack() as stack:
                # Enter existing lifespan context if it exists
                if existing_lifespan:
                    await stack.enter_async_context(existing_lifespan(app))

                # Enter additional lifespan contexts
                for lifespan_func in self._additional_lifespan_funcs:
                    await stack.enter_async_context(lifespan_func(app))

                yield  # Control is handed over to FastAPI for handling requests

        self._app.router.lifespan_context = combined_lifespan

    def get_app(self) -> FastAPI:
        """
        Returns the FastAPI app instance.

        :return: The encapsulated FastAPI app.
        """
        return self._app

    @staticmethod
    def create_router(
        prefix: str = "", tags: Optional[list[str]] = None, **kwargs
    ) -> APIRouter:
        """
        Creates a new APIRouter instance and registers it with the app.

        :param prefix: A string to be added to all route paths in the router.
        :param tags: A list of strings for tagging routes.
        :return: An APIRouter instance.
        """
        router = APIRouter(prefix=prefix, tags=tags, **kwargs)

        return router

    def include_router(self, router: APIRouter) -> None:
        """
        Includes an existing APIRouter into the FastAPI app.

        :param router: An APIRouter instance.
        """
        self._app.include_router(router)
        self._routers.append(router)

    def get_routers(self) -> list[APIRouter]:
        """
        Returns a list of all registered routers.

        :return: A list of APIRouter instances.
        """
        return self._routers
