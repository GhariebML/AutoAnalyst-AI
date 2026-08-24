"""Centralized LLM service providing retries, fallbacks, structured output validation, and observability."""

from __future__ import annotations

import json
import logging
import os
import re
import time
import uuid
from typing import Any, TypeVar

from pydantic import BaseModel

from autoanalyst.llm.provider import LLMProvider, OpenRouterProvider
from autoanalyst.llm.router import ModelRouter
from autoanalyst.llm.tracker import GLOBAL_USAGE_TRACKER, LLMUsageTracker
from autoanalyst.llm.types import LLMMessage, LLMRecord, LLMResponse, LLMUsage, TaskCategory

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMUnavailableError(Exception):
    """Raised when the LLM service is disabled or credentials are not configured."""

    pass


class LLMService:
    """Centralized LLM Gateway managing provider communication, retries, fallbacks, and schema validation."""

    def __init__(
        self,
        provider: LLMProvider | None = None,
        router: ModelRouter | None = None,
        tracker: LLMUsageTracker | None = None,
        enabled: bool | None = None,
        max_retries: int = 3,
        base_backoff_sec: float = 1.0,
        timeout: float = 60.0,
    ) -> None:
        self.provider = provider or OpenRouterProvider()
        self.router = router or ModelRouter()
        self.tracker = tracker or GLOBAL_USAGE_TRACKER

        if enabled is not None:
            self._enabled = enabled
        else:
            env_val = os.environ.get("AUTOANALYST_LLM_ENABLED", "true").strip().lower()
            self._enabled = env_val in ("1", "true", "yes", "on")

        self.max_retries = max_retries
        self.base_backoff_sec = base_backoff_sec
        self.timeout = timeout

    @property
    def is_available(self) -> bool:
        """Check if LLM execution is enabled and credentials are configured."""
        return self._enabled and self.provider.is_configured()

    def generate(
        self,
        task: TaskCategory | str,
        messages: list[LLMMessage],
        response_model: type[T] | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        run_id: str | None = None,
        agent_name: str | None = None,
    ) -> LLMResponse:
        """Generate response with automated retry, fallback model cascading, and schema parsing."""
        if not self.is_available:
            raise LLMUnavailableError("LLM service is disabled or missing valid API credentials.")

        task_category = TaskCategory(task) if isinstance(task, str) else task
        primary_model = self.router.resolve_model(task_category)
        fallback_model = self.router.resolve_fallback_model(task_category)

        # Prepare messages and format payload
        formatted_messages = list(messages)
        response_format = None
        if response_model is not None:
            response_format = {"type": "json_object"}
            # Ensure system or user prompt requests JSON conforming to model schema
            schema_hint = f"\n\nCRITICAL: Return valid JSON adhering strictly to the schema:\n{json.dumps(response_model.model_json_schema(), indent=2)}"
            formatted_messages[-1] = LLMMessage(
                role=formatted_messages[-1].role,
                content=formatted_messages[-1].content + schema_hint,
                name=formatted_messages[-1].name,
            )

        # 1. Attempt generation with Primary Model
        try:
            return self._execute_with_retry(
                model=primary_model,
                messages=formatted_messages,
                task_category=task_category,
                response_model=response_model,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
                run_id=run_id,
                agent_name=agent_name,
            )
        except Exception as primary_err:
            logger.warning(
                "Primary model '%s' failed for task %s: %s. Attempting fallback model '%s'...",
                primary_model,
                task_category.value,
                primary_err,
                fallback_model,
            )

            # 2. Attempt generation with Fallback Model
            try:
                fallback_res = self._execute_with_retry(
                    model=fallback_model,
                    messages=formatted_messages,
                    task_category=task_category,
                    response_model=response_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format=response_format,
                    run_id=run_id,
                    agent_name=agent_name,
                    is_fallback=True,
                )
                logger.info("Fallback model '%s' succeeded for task %s.", fallback_model, task_category.value)
                return fallback_res
            except Exception as fallback_err:
                logger.error(
                    "Both primary ('%s') and fallback ('%s') models failed for task %s: %s",
                    primary_model,
                    fallback_model,
                    task_category.value,
                    fallback_err,
                )
                raise RuntimeError(
                    f"LLM generation failed across primary and fallback models. Error: {fallback_err}"
                ) from fallback_err

    def _execute_with_retry(
        self,
        model: str,
        messages: list[LLMMessage],
        task_category: TaskCategory,
        response_model: type[T] | None,
        temperature: float,
        max_tokens: int,
        response_format: dict[str, Any] | None,
        run_id: str | None,
        agent_name: str | None,
        is_fallback: bool = False,
    ) -> LLMResponse:
        """Execute request with exponential backoff on transient errors."""
        last_exception = None
        req_id = f"llm_req_{uuid.uuid4().hex[:10]}"

        for attempt in range(1, self.max_retries + 1):
            start_time = time.perf_counter()
            try:
                response = self.provider.generate(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format=response_format,
                    timeout=self.timeout,
                )
                duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

                # Parse structured output if schema requested
                if response_model is not None:
                    parsed_obj = self._parse_json_payload(response.content, response_model)
                    response.parsed = parsed_obj

                # Record telemetry metrics
                status = "fallback" if is_fallback else "success"
                self.tracker.record_request(
                    LLMRecord(
                        request_id=req_id,
                        run_id=run_id,
                        agent_name=agent_name,
                        task_category=task_category.value,
                        model=model,
                        provider=self.provider.name,
                        status=status,
                        duration_ms=duration_ms,
                        usage=response.usage,
                    )
                )
                return response

            except Exception as exc:
                last_exception = exc
                duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
                err_str = str(exc).lower()

                # Determine if error is transient (429, 5xx, timeout)
                is_transient = any(
                    code in err_str
                    for code in ("429", "500", "502", "503", "504", "timeout", "rate limit", "connection")
                )

                if is_transient and attempt < self.max_retries:
                    sleep_time = self.base_backoff_sec * (2 ** (attempt - 1))
                    logger.warning(
                        "Transient error on attempt %d/%d for model %s: %s. Retrying in %.1fs...",
                        attempt,
                        self.max_retries,
                        model,
                        exc,
                        sleep_time,
                    )
                    time.sleep(sleep_time)
                else:
                    # Non-transient or retries exhausted
                    self.tracker.record_request(
                        LLMRecord(
                            request_id=req_id,
                            run_id=run_id,
                            agent_name=agent_name,
                            task_category=task_category.value,
                            model=model,
                            provider=self.provider.name,
                            status="error",
                            duration_ms=duration_ms,
                            usage=LLMUsage(),
                            error_message=str(exc),
                        )
                    )
                    raise exc

        raise last_exception or RuntimeError(f"Request failed for model {model}")

    def _parse_json_payload(self, text: str, model_cls: type[T]) -> T:
        """Safely extract and parse JSON payload into the requested Pydantic model."""
        cleaned = text.strip()
        # Remove markdown code fences if present
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
            cleaned = cleaned.strip()

        try:
            return model_cls.model_validate_json(cleaned)
        except Exception as exc:
            # Attempt regex search for first valid JSON object
            match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
            if match:
                try:
                    return model_cls.model_validate_json(match.group(1))
                except Exception:
                    pass
            logger.error("Failed to validate LLM response into schema %s. Raw text: %s", model_cls.__name__, text)
            raise ValueError(f"LLM output could not be validated into schema {model_cls.__name__}: {exc}") from exc


# Global Singleton Service
GLOBAL_LLM_SERVICE = LLMService()
