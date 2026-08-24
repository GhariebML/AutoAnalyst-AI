"""Application configuration and environment settings for AutoAnalyst AI backend."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings loaded from environment or .env file."""

    APP_NAME: str = "AutoAnalyst AI Backend"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # Storage paths
    STORAGE_DIR: Path = Path(".autoanalyst/storage")
    DATABASE_URL: str = "sqlite:///.autoanalyst/autoanalyst.db"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://localhost:8501",
        "http://localhost:8502",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8501",
        "http://127.0.0.1:8502",
    ]

    # LLM Settings
    AUTOANALYST_LLM_ENABLED: bool = True
    AUTOANALYST_LLM_PROVIDER: Literal["openrouter", "openai", "anthropic", "google", "gemini", "ollama", "mock"] = "openrouter"
    AUTOANALYST_LLM_MODEL: str = "openai/gpt-4o-mini"

    # OpenRouter Specific Settings
    OPENROUTER_API_KEY: str | None = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "openai/gpt-4o-mini"
    OPENROUTER_FALLBACK_MODEL: str = "anthropic/claude-3.5-haiku"
    OPENROUTER_TIMEOUT: float = 60.0
    OPENROUTER_MAX_RETRIES: int = 3
    OPENROUTER_TEMPERATURE: float = 0.2
    OPENROUTER_MAX_TOKENS: int = 2048
    OPENROUTER_SITE_URL: str = "https://github.com/GhariebML/AutoAnalyst-AI"
    OPENROUTER_APP_NAME: str = "AutoAnalyst AI"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
