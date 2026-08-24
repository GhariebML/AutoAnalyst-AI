"""Provider abstraction layer for OpenRouter and pluggable LLM backends."""

from __future__ import annotations

import json
import logging
import os
import time
from abc import ABC, abstractmethod
from typing import Any

import httpx

from autoanalyst.llm.types import LLMMessage, LLMResponse, LLMUsage

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract contract for LLM inference providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name identifier."""
        ...

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if provider credentials and network configurations are available."""
        ...

    @abstractmethod
    def generate(
        self,
        messages: list[LLMMessage],
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        response_format: dict[str, Any] | None = None,
        timeout: float = 60.0,
    ) -> LLMResponse:
        """Generate a chat completion response synchronously."""
        ...


class OpenRouterProvider(LLMProvider):
    """Production provider integrating OpenRouter as a centralized multi-model gateway."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        site_url: str | None = None,
        app_name: str | None = None,
    ) -> None:
        self._api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self._base_url = (
            base_url
            or os.environ.get("OPENROUTER_BASE_URL")
            or "https://openrouter.ai/api/v1"
        ).rstrip("/")
        self._site_url = site_url or os.environ.get("OPENROUTER_SITE_URL", "https://github.com/GhariebML/AutoAnalyst-AI")
        self._app_name = app_name or os.environ.get("OPENROUTER_APP_NAME", "AutoAnalyst AI")

    @property
    def name(self) -> str:
        return "openrouter"

    def is_configured(self) -> bool:
        key = self._api_key or os.environ.get("OPENROUTER_API_KEY")
        return bool(key and len(key.strip()) > 5)

    def _get_headers(self) -> dict[str, str]:
        key = self._api_key or os.environ.get("OPENROUTER_API_KEY")
        if not key:
            raise ValueError("OPENROUTER_API_KEY is not configured in the environment.")
        return {
            "Authorization": f"Bearer {key.strip()}",
            "HTTP-Referer": self._site_url,
            "X-Title": self._app_name,
            "Content-Type": "application/json",
        }

    def generate(
        self,
        messages: list[LLMMessage],
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        response_format: dict[str, Any] | None = None,
        timeout: float = 60.0,
    ) -> LLMResponse:
        start_time = time.perf_counter()
        payload: dict[str, Any] = {
            "model": model,
            "messages": [m.model_dump(exclude_none=True) for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        url = f"{self._base_url}/chat/completions"
        headers = self._get_headers()

        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, headers=headers, json=payload)
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

            if resp.status_code != 200:
                error_msg = f"OpenRouter API error (HTTP {resp.status_code}): {resp.text}"
                logger.error("OpenRouter request failed for model %s: %s", model, resp.text)
                raise RuntimeError(error_msg)

            data = resp.json()

        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError(f"OpenRouter returned empty choices: {data}")

        choice = choices[0]
        content = choice.get("message", {}).get("content", "")

        raw_usage = data.get("usage", {})
        prompt_tokens = raw_usage.get("prompt_tokens", 0)
        completion_tokens = raw_usage.get("completion_tokens", 0)
        total_tokens = raw_usage.get("total_tokens", prompt_tokens + completion_tokens)

        return LLMResponse(
            content=content,
            model=model,
            provider="openrouter",
            usage=LLMUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            ),
            duration_ms=duration_ms,
        )


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for unit tests, offline validation, and deterministic simulations."""

    def __init__(self, predefined_responses: dict[str, str] | None = None) -> None:
        self.predefined_responses = predefined_responses or {}
        self.call_history: list[dict[str, Any]] = []

    @property
    def name(self) -> str:
        return "mock"

    def is_configured(self) -> bool:
        return True

    def generate(
        self,
        messages: list[LLMMessage],
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        response_format: dict[str, Any] | None = None,
        timeout: float = 60.0,
    ) -> LLMResponse:
        self.call_history.append(
            {
                "messages": messages,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "response_format": response_format,
            }
        )
        last_message = messages[-1].content if messages else ""

        # Match predefined response or generate structured mock
        content = None
        for key, val in self.predefined_responses.items():
            if key in last_message:
                content = val
                break

        if content is None:
            if response_format and response_format.get("type") == "json_object":
                content = json.dumps(
                    {
                        "summary": "Mock LLM reasoning response.",
                        "confidence": 0.95,
                        "recommendations": ["Proceed with data analysis.", "Inspect anomalies."],
                    }
                )
            else:
                content = "Mock LLM response formulation with evidence-based reasoning."

        return LLMResponse(
            content=content,
            model=model,
            provider="mock",
            usage=LLMUsage(prompt_tokens=50, completion_tokens=30, total_tokens=80),
            duration_ms=10.0,
        )
