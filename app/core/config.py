import json
import os
from typing import Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AURA POS Backend"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"

    # Database (fallback safely if environment variable is unset or empty string)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/aura_pos"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: Any) -> str:
        if not v or not str(v).strip():
            return "postgresql://postgres:postgres@localhost:5432/aura_pos"
        return str(v)

    # JWT Authentication
    JWT_SECRET: str = "super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    JWT_REFRESH_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    @field_validator("JWT_SECRET", mode="before")
    @classmethod
    def validate_jwt_secret(cls, v: Any) -> str:
        if not v or not str(v).strip():
            return "super-secret-key-change-in-production"
        return str(v)

    # LLM & External Services
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    EXTERNAL_EVENT_API_KEY: str = os.getenv("EXTERNAL_EVENT_API_KEY", "")

    # Hermes API
    HERMES_API_SERVER_KEY: str = os.getenv("HERMES_API_SERVER_KEY", "")
    HERMES_API_URL: str = "http://127.0.0.1:8642"

    @field_validator("HERMES_API_URL", mode="before")
    @classmethod
    def validate_hermes_url(cls, v: Any) -> str:
        if not v or not str(v).strip():
            return "http://127.0.0.1:8642"
        return str(v)

    # GOOGLE API
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")  
    GOOGLE_REFRESH_TOKEN: str = os.getenv("GOOGLE_REFRESH_TOKEN", "")

    # CORS (supports list, JSON string array, and comma-separated strings)
    CORS_ORIGINS: list[str] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            v_stripped = v.strip()
            if v_stripped.startswith("[") and v_stripped.endswith("]"):
                try:
                    return json.loads(v_stripped)
                except Exception:
                    pass
            return [origin.strip() for origin in v_stripped.split(",") if origin.strip()]
        if isinstance(v, list):
            return v
        return ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
