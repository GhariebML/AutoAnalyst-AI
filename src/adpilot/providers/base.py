"""Base provider interface definition."""

from __future__ import annotations

import abc
from langchain_core.language_models.chat_models import BaseChatModel


class LLMProvider(abc.ABC):
    """Abstract base class for all LLM providers."""

    @abc.abstractmethod
    def get_model(self) -> BaseChatModel:
        """Return the initialized LangChain chat model."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_structured_output_kwargs(self) -> dict:
        """Return provider-specific parameters for model.with_structured_output()."""
        raise NotImplementedError

    def get_fallback_models(self) -> list[BaseChatModel]:
        """Return a list of fallback models, if any."""
        return []
