"""Hugging Face provider implementation."""

from __future__ import annotations

from langchain_openai import ChatOpenAI
from ..core.config import get_config
from .base import LLMProvider
from pydantic import SecretStr


class HuggingFaceProvider(LLMProvider):
    """HuggingFace Inference Endpoints LLM provider."""

    def get_model(self) -> ChatOpenAI:
        settings = get_config()
        if not settings.hf_token:
            raise ValueError("HF_TOKEN is required when LLM_PROVIDER=huggingface.")
        return ChatOpenAI(
            api_key=SecretStr(settings.hf_token),
            model=settings.hf_model,
            base_url=settings.hf_base_url,
            temperature=settings.temperature,
            max_tokens=4096,
            max_retries=0,
        )

    def get_fallback_models(self) -> list:
        try:
            from .openrouter_provider import OpenRouterProvider
            return [OpenRouterProvider().get_model()]
        except Exception:
            return []

    def get_structured_output_kwargs(self) -> dict:
        return {"include_raw": False}
