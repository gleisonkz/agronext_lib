from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, APIRouter, BackgroundTasks, Response, status

from agronext_api.config.settings import settings

from .database import close_db, init_db
from .exceptions import init_error_handling
from .extensions import init_extensions
from .integrations import close_integrations, init_integrations
from .logger import close_logger, get_logger, init_logger
from .messaging import close_messaging, init_messaging
from .middlewares import init_middlewares
from .security import init_security


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    lifespan_logger = get_logger("lifespan")

    await init_messaging(app)
    lifespan_logger.info("Messaging integration initialized")

    try:
        await init_db()
        lifespan_logger.info("Database ORM initialized")
    except BaseException as e:
        lifespan_logger.error(f"Error initializing database: {type(e).__name__}")
        raise e

    await init_integrations()

    yield

    close_integrations()
    lifespan_logger.info("Integrations closed")

    await close_db()
    lifespan_logger.info("Database ORM closed")

    close_messaging()
    lifespan_logger.info("Messaging closed")

    close_logger()

class AgronextAPI:
    def create_app(self, routers: list[FastAPI]) -> FastAPI:
        log_level = "DEBUG" if settings.DEBUG else settings.LOG_LEVEL
        init_logger(log_level)

        app = FastAPI(
            title="Agronext Backend",
            description="Backend for Agronext Platform",
            version=settings.API_VERSION,
            lifespan=lifespan,
        )

        init_error_handling(app)
        init_security(app)
        init_extensions(app)
        init_middlewares(app)
        
        for router in routers:
            app.add_router(router)

        return app
