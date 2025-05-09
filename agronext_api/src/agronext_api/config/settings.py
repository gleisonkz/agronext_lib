from ..config.base_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = True

    LOG_LEVEL: str = "INFO"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    APP_DOMAIN: str = "localhost:3000"


api_settings = Settings()
