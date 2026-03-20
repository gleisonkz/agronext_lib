from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict  # noqa F401
from pydantic import Field, computed_field


class BaseSettings(PydanticBaseSettings):
    pass


__all__ = ["BaseSettings", "SettingsConfigDict", "Field", "computed_field"]
