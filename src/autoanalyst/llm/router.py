"""Centralized model routing architecture with task-specific resolution and fallbacks."""

from __future__ import annotations

import os
from typing import Mapping

from autoanalyst.llm.types import TaskCategory


class ModelRouter:
    """Resolves primary and fallback models per task category based on environment configuration."""

    def __init__(
        self,
        default_model: str | None = None,
        fallback_model: str | None = None,
        task_overrides: Mapping[TaskCategory, str] | None = None,
    ) -> None:
        self.default_model = (
            default_model
            or os.environ.get("OPENROUTER_MODEL")
            or os.environ.get("AUTOANALYST_LLM_MODEL")
            or "openai/gpt-4o-mini"
        )
        self.fallback_model = (
            fallback_model
            or os.environ.get("OPENROUTER_FALLBACK_MODEL")
            or "anthropic/claude-3.5-haiku"
        )
        self.task_overrides = dict(task_overrides or {})

    def resolve_model(self, task: TaskCategory | str) -> str:
        """Resolve the primary model for the given task category."""
        category = TaskCategory(task) if isinstance(task, str) else task
        if category in self.task_overrides:
            return self.task_overrides[category]

        # Check environment variable for specific task override
        env_key = f"OPENROUTER_MODEL_{category.value.upper()}"
        if os.environ.get(env_key):
            return os.environ[env_key]

        return self.default_model

    def resolve_fallback_model(self, task: TaskCategory | str) -> str:
        """Resolve the fallback model if the primary model encounters errors."""
        category = TaskCategory(task) if isinstance(task, str) else task
        env_key = f"OPENROUTER_FALLBACK_MODEL_{category.value.upper()}"
        if os.environ.get(env_key):
            return os.environ[env_key]
        return self.fallback_model

    def set_task_model(self, task: TaskCategory, model_name: str) -> None:
        """Dynamically set model for a specific task category."""
        self.task_overrides[task] = model_name
