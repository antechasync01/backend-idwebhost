import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AURA POS Backend"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/aura_pos"
    )

    # JWT Authentication
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    JWT_REFRESH_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # LLM & External Services
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    EXTERNAL_EVENT_API_KEY: str = os.getenv("EXTERNAL_EVENT_API_KEY", "")

    # Hermes API
    HERMES_API_SERVER_KEY: str = os.getenv("HERMES_API_SERVER_KEY", "")
    HERMES_API_URL: str = os.getenv("HERMES_API_URL", "http://127.0.0.1:8642")

    # GOOGLE API
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")  
    GOOGLE_REFRESH_TOKEN: str = os.getenv("GOOGLE_REFRESH_TOKEN", "")

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
