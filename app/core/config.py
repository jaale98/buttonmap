from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl, Field

class Settings(BaseSettings):
    DATABASE_URL: AnyUrl = Field(
        "postgresql+psycopg://postgres:postgres@localhost:5432/appdb",
        description="SQLAlchemy URL. For local dev before Docker, localhost is fine.",
    ) # type: ignore
    ENV: str = Field("dev", description="Environment name: dev/test/prod")
    LOG_LEVEL: str = Field("info", description="Logging level")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings() # type: ignore

settings = get_settings()