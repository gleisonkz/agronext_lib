from ..config.base_settings import BaseSettings

class DatabaseSettings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USERNAME: str = "postgres"
    DB_PASSWORD: str = "rootpassword"
    DB_DATABASE: str = "postgres"

    DB_MODELS: list[str] = [
        "agronext_database.models.tables",
        "agronext_database.models.views",
        "aerich.models",
    ]

database_settings = DatabaseSettings()

