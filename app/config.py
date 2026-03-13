from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Crypto Price Service"
    api_v1_prefix: str = "/api"

    db_host: str = Field("db", env="DB_HOST")
    db_port: int = Field(5432, env="DB_PORT")
    db_user: str = Field("crypto_user", env="DB_USER")
    db_password: str = Field("crypto_password", env="DB_PASSWORD")
    db_name: str = Field("crypto_db", env="DB_NAME")

    celery_broker_url: str = Field(
        "redis://redis:6379/0",
        env="CELERY_BROKER_URL",
    )
    celery_result_backend: str = Field(
        "redis://redis:6379/1",
        env="CELERY_RESULT_BACKEND",
    )

    deribit_base_url: str = Field(
        "https://www.deribit.com/api/v2",
        env="DERIBIT_BASE_URL",
    )

    # Tickers / indices we want to track on Deribit
    tracked_indices: tuple[str, ...] = ("btc_usd", "eth_usd")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def database_url_async(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def database_url_sync(self) -> str:
        # Used by Alembic or synchronous tools if needed
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return application settings (cached per process). Avoids module-level global."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

