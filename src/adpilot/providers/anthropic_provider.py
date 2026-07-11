"""Anthropic (Claude) LLM Provider."""

from __future__ import annotations

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel

from ..core.config import get_config
from .base import LLMProvider


class AnthropicProvider(LLMProvider):
    """Provides access to Anthropic Claude models."""

    def __init__(self) -> None:
        self.settings = get_config()

    def get_model(self) -> BaseChatModel:
        """Initialize and return the ChatAnthropic model."""
        return ChatAnthropic(
            model=self.settings.anthropic_model,
            api_key=self.settings.anthropic_api_key,
            temperature=self.settings.temperature,
            max_retries=0,  # Retries handled by ProviderRouter
        )

    def get_structured_output_kwargs(self) -> dict:
        """Claude supports structured output via tools."""
        return {}
