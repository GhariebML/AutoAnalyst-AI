"""Provider factory to select active LLM provider."""

from __future__ import annotations

from .base import LLMProvider


def get_active_provider() -> LLMProvider:
    """Return the ProviderRouter which handles LLM selection and routing."""
    from ..services.provider_router import ProviderRouter
    return ProviderRouter()
