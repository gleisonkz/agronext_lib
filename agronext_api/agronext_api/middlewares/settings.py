from ..config.base_settings import BaseSettings

class MiddlewareSettings(BaseSettings):
    ALLOWED_HOSTS: list[str] = ["*"]
    ALLOWED_ORIGINS: list[str] = ["*"]


middleware_settings = MiddlewareSettings()

