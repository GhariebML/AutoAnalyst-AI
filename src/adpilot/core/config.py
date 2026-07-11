"""Application configuration."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AdPilotConfig(BaseSettings):
    """Application configuration loaded from environment variables and .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_provider: str = Field(default="openrouter", alias="LLM_PROVIDER")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", alias="OPENAI_MODEL")
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="openrouter/free", alias="OPENROUTER_MODEL")
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        alias="OPENROUTER_BASE_URL",
    )
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-5-sonnet-latest", alias="ANTHROPIC_MODEL")
    ollama_base_url: str = Field(default="http://localhost:11434/v1", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="qwen3:8b", alias="OLLAMA_MODEL")
    hf_token: str = Field(default="", alias="HF_TOKEN")
    hf_model: str = Field(default="deepseek-ai/DeepSeek-R1", alias="HF_MODEL")
    hf_base_url: str = Field(default="https://router.huggingface.co/v1", alias="HF_BASE_URL")
    temperature: float = Field(default=0.2, alias="TEMPERATURE")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    serpapi_api_key: str = Field(default="", alias="SERPAPI_API_KEY")
    cloudinary_cloud_name: str = Field(default="", alias="CLOUDINARY_CLOUD_NAME")
    cloudinary_api_key: str = Field(default="", alias="CLOUDINARY_API_KEY")
    cloudinary_api_secret: str = Field(default="", alias="CLOUDINARY_API_SECRET")
    database_url: str = Field(default="sqlite+aiosqlite:///./adpilot.db", alias="DATABASE_URL")
    memory_backend: str = Field(default="memory", alias="MEMORY_BACKEND")

    # Qdrant RAG DB
    qdrant_mode: str = Field(default="local", alias="QDRANT_MODE")
    qdrant_path: str = Field(default="./storage/qdrant", alias="QDRANT_PATH")
    qdrant_url: str = Field(default="", alias="QDRANT_URL")
    qdrant_api_key: str = Field(default="", alias="QDRANT_API_KEY")
    
    mongodb_url: str = Field(default="mongodb://localhost:27017", alias="MONGODB_URL")

    # Security & CORS
    api_key: str = Field(default="", alias="ADPILOT_API_KEY")
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:3001,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173",
        alias="ALLOWED_ORIGINS",
    )

    @property
    def model_name(self) -> str:
        """Backward-compatible alias for older code/tests."""
        return self.openai_model


@lru_cache(maxsize=1)
def get_config() -> "AdPilotConfig":
    """Return cached settings."""
    return AdPilotConfig()
