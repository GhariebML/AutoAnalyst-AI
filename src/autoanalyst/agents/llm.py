"""Optional LLM access for the narration layer.

Design contract (documented in docs/agentic_architecture_langchain_langgraph.md):
- LLM usage is fully optional; when disabled the system runs with zero model
  calls and rule-based fallbacks.
- Configuration comes exclusively from environment variables / ``.env``.
- Provider packages are lazy-imported so the core install never needs them.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Mapping
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel

logger = logging.getLogger(__name__)

TRUE_VALUES = {"1", "true", "yes", "on"}
PROVIDER_KEY_VARS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}


@dataclass(frozen=True)
class LLMSettings:
    """Resolved LLM configuration from the environment."""

    enabled: bool
    provider: str = "openai"
    model: str | None = None


def load_llm_settings(env: Mapping[str, str] | None = None) -> LLMSettings:
    """Read LLM settings from the environment (``.env`` is loaded once)."""
    if env is None:
        load_dotenv()
        env = os.environ
    enabled = str(env.get("AUTOANALYST_LLM_ENABLED", "")).strip().lower() in TRUE_VALUES
    provider = str(env.get("AUTOANALYST_LLM_PROVIDER", "openai")).strip().lower() or "openai"
    model = str(env.get("AUTOANALYST_LLM_MODEL", "")).strip() or None
    return LLMSettings(enabled=enabled, provider=provider, model=model)


def create_llm(settings: LLMSettings | None = None) -> BaseChatModel | None:
    """Instantiate the configured chat model, or ``None`` when disabled.

    Returns ``None`` (never raises) when LLM narration is disabled so callers
    can fall back to deterministic narration. Misconfiguration with narration
    explicitly enabled raises ``RuntimeError`` with actionable guidance.
    """
    resolved = settings or load_llm_settings()
    if not resolved.enabled:
        return None
    if resolved.provider not in PROVIDER_KEY_VARS:
        raise RuntimeError(
            f"Unsupported AUTOANALYST_LLM_PROVIDER '{resolved.provider}'. "
            f"Supported providers: {sorted(PROVIDER_KEY_VARS)}."
        )

    key_var = PROVIDER_KEY_VARS[resolved.provider]
    if not os.environ.get(key_var):
        raise RuntimeError(
            f"LLM narration is enabled but {key_var} is not set. "
            "Set it in your environment or .env file."
        )

    try:
        if resolved.provider == "openai":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(model=resolved.model or "gpt-4o-mini")
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=resolved.model or "claude-3-5-haiku-latest")
    except ImportError as exc:
        raise RuntimeError(
            f"Provider package for '{resolved.provider}' is not installed. "
            "Install it with: pip install 'autoanalyst-ai[llm]'"
        ) from exc


__all__ = ["LLMSettings", "create_llm", "load_llm_settings"]
