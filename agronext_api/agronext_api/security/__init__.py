from fastapi import FastAPI

from ..config.settings import api_settings
from ..middlewares.security import CORSMiddleware, TrustedHostMiddleware
from ..middlewares.settings import middleware_settings


def init_security(app: FastAPI) -> None:
    if api_settings.DEBUG:
        return

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=middleware_settings.ALLOWED_HOSTS)
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_origins=middleware_settings.ALLOWED_ORIGINS,
    )
