from ...config.base_settings import BaseSettings
from pydantic import Field


class AuthSettings(BaseSettings):
    CLIENT_ID: str = Field(default="", description="client id", env="AUTH_CLIENT_ID")
    CLIENT_SECRET: str = Field(default="", description="client secret", env="AUTH_CLIENT_SECRET")
    AUTHORITY: str = Field(default="", description="client secret", env="AUTH_AUTHORITY")
    SECRET_KEY: str = Field(default="Sua secret Key", description="secret key", env="AUTH_SECRET_KEY")

auth_settings = AuthSettings()