"""OpenAI provider implementation."""

from __future__ import annotations

from langchain_openai import ChatOpenAI
from ..core.config import get_config
from .base import LLMProvider
from pydantic import SecretStr


class OpenAIProvider(LLMProvider):
    """OpenAI native LLM provider."""

    def get_model(self) -> ChatOpenAI:
        settings = get_config()
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")
        return ChatOpenAI(
            api_key=SecretStr(settings.openai_api_key),
            model=settings.openai_model,
            temperature=settings.temperature,
            max_retries=0,  # Retries handled manually in base_agent
        )

    def get_structured_output_kwargs(self) -> dict:
        return {"method": "function_calling"}
