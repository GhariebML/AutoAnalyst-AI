"""LLM client helpers.

All agents use ``get_chat_model()`` via ``BaseAgent.call_llm()``.  The legacy
``LLMClient`` wrapper was removed because it relied on deprecated OpenAI SDK v0
APIs (``openai.ChatCompletion.acreate``, ``openai.error.*``) that are
incompatible with ``openai >= 1.0``.
"""

from __future__ import annotations

import logging
from ..providers.factory import get_active_provider

logger = logging.getLogger(__name__)


def mask_key(key: str | None) -> str:
    """Securely mask an API key for logging or exceptions."""
    if not key:
        return "None"
    if len(key) <= 8:
        return "****"
    return f"{key[:4]}****{key[-4:]}"


def get_chat_model():
    """Create a configured LangChain chat model.

    Delegates model initialization to the active provider instance.
    """
    return get_active_provider().get_model()
