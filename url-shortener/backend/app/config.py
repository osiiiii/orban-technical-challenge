"""Application configuration, loaded from environment variables.

Uses pydantic-settings so that values can be overridden via a .env file
or real environment variables without touching code.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Secret key required in the X-API-Key header to create/list/inspect URLs.
    api_key: str = "dev-secret-key-change-me"

    # SQLAlchemy database URL. Defaults to a local SQLite file.
    database_url: str = "sqlite:///./shortener.db"

    # Public base URL used when building the full short link returned to clients.
    # e.g. https://sho.rt  ->  https://sho.rt/abc123
    base_url: str = "http://localhost:8000"

    # Length of generated short codes.
    code_length: int = 6

    # Comma-separated list of origins allowed to call the API (the frontend).
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
