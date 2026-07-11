"""OpenRouter provider implementation."""

from __future__ import annotations

from langchain_openai import ChatOpenAI
from ..core.config import get_config
from .base import LLMProvider


from pydantic import SecretStr

class OpenRouterProvider(LLMProvider):
    """OpenRouter LLM provider."""

    def get_model(self) -> ChatOpenAI:
        settings = get_config()
        if not settings.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is required when LLM_PROVIDER=openrouter.")
        return ChatOpenAI(
            api_key=SecretStr(settings.openrouter_api_key),
            model=settings.openrouter_model,
            base_url=settings.openrouter_base_url,
            temperature=settings.temperature,
            max_tokens=4096,
            max_retries=0,
        )

    def get_structured_output_kwargs(self) -> dict:
        return {"include_raw": False}
