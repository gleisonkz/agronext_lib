from fastapi import FastAPI

from ..middlewares.security import CORSMiddleware, TrustedHostMiddleware
from ..middlewares.settings import middleware_settings
from ..logger import get_logger

logger = get_logger("api.security")


def init_security(app: FastAPI) -> None:
    if not middleware_settings.ALLOWED_HOSTS == ["*"]:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=middleware_settings.ALLOWED_HOSTS,
        )
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=middleware_settings.ALLOW_CREDENTIALS,
        allow_methods=middleware_settings.ALLOWED_METHODS,
        allow_headers=middleware_settings.ALLOWED_HEADERS,
        allow_origins=middleware_settings.ALLOWED_ORIGINS,
    )
    logger.debug(
        f"Configured Security with settings: {middleware_settings.model_dump()}"
    )
