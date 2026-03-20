from ..config.base_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class MiddlewareSettings(BaseSettings):
    model_config = SettingsConfigDict(
        prefix="API_",
        env_file=".env",
        extra="ignore",
    )
    ALLOWED_HEADERS: list[str] = Field(default_factory=lambda: ["*"])
    ALLOWED_METHODS: list[str] = Field(default_factory=lambda: ["*"])
    ALLOWED_HOSTS: list[str] = Field(default_factory=lambda: ["*"])
    ALLOWED_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])
    ALLOW_CREDENTIALS: bool = False


middleware_settings = MiddlewareSettings()
