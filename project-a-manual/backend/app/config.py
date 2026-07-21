from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    api_key: str = "dev-key-change-me"
    database_url: str = "sqlite:///./notes.db"
    cors_origins: str = "http://localhost:3000"


settings = Settings()
