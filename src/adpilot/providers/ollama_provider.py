"""Ollama Local LLM Provider."""

from __future__ import annotations

from langchain_community.chat_models import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel

from ..core.config import get_config
from .base import LLMProvider


class OllamaProvider(LLMProvider):
    """Provides access to local Ollama models."""

    def __init__(self) -> None:
        self.settings = get_config()

    def get_model(self) -> BaseChatModel:
        """Initialize and return the ChatOllama model."""
        return ChatOllama(
            model=self.settings.ollama_model,
            base_url=self.settings.ollama_base_url,
            temperature=self.settings.temperature,
            # max_retries=0  # ChatOllama usually handles its own retries, but we let ProviderRouter manage backoff
        )

    def get_structured_output_kwargs(self) -> dict:
        """Ollama supports structured output via JSON mode for certain models."""
        return {"format": "json"}
