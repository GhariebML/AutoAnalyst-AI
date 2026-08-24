"""Optional LLM access for the narration and conversational intelligence layer.

Design contract:
- LLM usage is fully optional; when disabled the system runs with zero model calls and rule-based fallbacks.
- Configuration comes exclusively from environment variables / ``.env``.
- Supports Google Gemini, OpenAI, Anthropic, and Ollama providers with lazy imports.
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
    "google": "GOOGLE_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "ollama": "",  # Local, doesn't require API key
}


@dataclass(frozen=True)
class LLMSettings:
    """Resolved LLM configuration from the environment."""

    enabled: bool
    provider: str = "openai"
    model: str | None = None
    temperature: float = 0.2


def load_llm_settings(env: Mapping[str, str] | None = None) -> LLMSettings:
    """Read LLM settings from the environment (``.env`` is loaded once)."""
    if env is None:
        load_dotenv()
        env = os.environ
    enabled = str(env.get("AUTOANALYST_LLM_ENABLED", "")).strip().lower() in TRUE_VALUES
    provider = str(env.get("AUTOANALYST_LLM_PROVIDER", "openai")).strip().lower() or "openai"
    model = str(env.get("AUTOANALYST_LLM_MODEL", "")).strip() or None
    try:
        temp = float(env.get("AUTOANALYST_LLM_TEMPERATURE", "0.2"))
    except ValueError:
        temp = 0.2
    return LLMSettings(enabled=enabled, provider=provider, model=model, temperature=temp)


def create_llm(settings: LLMSettings | None = None) -> BaseChatModel | None:
    """Instantiate the configured chat model, or ``None`` when disabled."""
    resolved = settings or load_llm_settings()
    if not resolved.enabled:
        return None

    provider = resolved.provider
    if provider not in PROVIDER_KEY_VARS:
        raise RuntimeError(
            f"Unsupported AUTOANALYST_LLM_PROVIDER '{provider}'. Supported providers: {sorted(PROVIDER_KEY_VARS)}."
        )

    key_var = PROVIDER_KEY_VARS[provider]
    if key_var and not (
        os.environ.get(key_var)
        or (provider in {"google", "gemini"} and os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    ):
        raise RuntimeError(
            f"LLM narration is enabled but {key_var} is not set. Set it in your environment or .env file."
        )

    try:
        if provider == "openai":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=resolved.model or "gpt-4o-mini",
                temperature=resolved.temperature,
            )

        if provider == "anthropic":
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                model=resolved.model or "claude-3-5-haiku-latest",
                temperature=resolved.temperature,
            )

        if provider in {"google", "gemini"}:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI

                api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
                return ChatGoogleGenerativeAI(
                    model=resolved.model or "gemini-1.5-flash",
                    google_api_key=api_key,
                    temperature=resolved.temperature,
                )
            except ImportError:
                pass

        if provider == "ollama":
            try:
                from langchain_community.chat_models import ChatOllama

                return ChatOllama(
                    model=resolved.model or "llama3.2",
                    temperature=resolved.temperature,
                )
            except ImportError:
                pass

    except ImportError as exc:
        raise RuntimeError(
            f"Provider package for '{provider}' is not installed. Install it with: pip install 'autoanalyst-ai[llm]'"
        ) from exc

    raise RuntimeError(f"Could not initialize LLM provider '{provider}'.")


__all__ = ["LLMSettings", "create_llm", "load_llm_settings"]
