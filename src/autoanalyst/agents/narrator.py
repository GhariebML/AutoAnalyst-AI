"""Narration services: LLM-enriched storytelling with deterministic fallbacks.

Every public function follows the same contract:
- pass ``llm=None`` (or run with ``AUTOANALYST_LLM_ENABLED`` unset) and the
  function produces a useful rule-based result without any model call
- pass a chat model (real or a test double) to get narrative text
- any LLM failure degrades to the deterministic fallback, never an exception
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

import pandas as pd
from langchain_core.language_models.chat_models import BaseChatModel

from autoanalyst.agents.prompts import ADVISOR_PROMPT, INSIGHTS_PROMPT, SUMMARY_PROMPT
from autoanalyst.insights.insight_generator import generate_dataset_insights

logger = logging.getLogger(__name__)

_MAX_PROMPT_CHARS = 4000


@dataclass
class Narration:
    """Produced narration plus its provenance."""

    texts: list[str] = field(default_factory=list)
    source: str = "rules"  # "rules" | "llm"


def narrate_insights(
    df: pd.DataFrame,
    profile: dict[str, Any],
    model_results: dict[str, Any] | None = None,
    evaluation_results: dict[str, Any] | None = None,
    *,
    llm: BaseChatModel | None = None,
    max_insights: int = 8,
) -> Narration:
    """Produce headline findings; LLM-narrated when available, rules otherwise."""
    fallback = Narration(texts=generate_dataset_insights(df), source="rules")
    if llm is None:
        return fallback

    prompt = INSIGHTS_PROMPT.format(
        max_insights=max_insights,
        profile_json=_truncate(json.dumps(profile, default=str)),
        model_json=_truncate(json.dumps(model_results or {}, default=str)),
        evaluation_json=_truncate(json.dumps(_scalar_metrics(evaluation_results), default=str)),
    )
    try:
        response = llm.invoke(prompt)
        texts = _parse_bullets(_content(response), limit=max_insights)
    except Exception as exc:
        logger.warning("LLM insight narration failed; using rule-based insights: %s", exc)
        return fallback

    if not texts:
        logger.warning("LLM insight narration returned no usable lines; using rule-based fallback.")
        return fallback
    return Narration(texts=texts, source="llm")


def advisor_note(
    model_results: dict[str, Any] | None,
    evaluation_results: dict[str, Any] | None,
    *,
    llm: BaseChatModel | None = None,
) -> str:
    """One actionable next-step note for the analyst."""
    if llm is not None:
        prompt = ADVISOR_PROMPT.format(
            model_json=_truncate(json.dumps(model_results or {}, default=str)),
            evaluation_json=_truncate(json.dumps(_scalar_metrics(evaluation_results), default=str)),
        )
        try:
            text = _content(llm.invoke(prompt)).strip()
            if text:
                return text
        except Exception as exc:
            logger.warning("LLM advisory failed; using deterministic advice: %s", exc)
    return _rule_based_advice(model_results, evaluation_results)


def executive_summary(
    profile: dict[str, Any],
    insights: list[str],
    evaluation_results: dict[str, Any] | None = None,
    *,
    llm: BaseChatModel | None = None,
) -> str:
    """Short report-level summary; deterministic when no model is available."""
    if llm is not None:
        insights_block = "\n".join(f"- {insight}" for insight in insights[:6]) or "- (none)"
        prompt = SUMMARY_PROMPT.format(
            profile_json=_truncate(json.dumps(profile, default=str)),
            insights_block=insights_block,
        )
        try:
            text = _content(llm.invoke(prompt)).strip()
            if text:
                return text
        except Exception as exc:
            logger.warning("LLM summary failed; using deterministic summary: %s", exc)

    rows = profile.get("rows", "?")
    columns = profile.get("columns", "?")
    metric_clause = ""
    metrics = _scalar_metrics(evaluation_results)
    if metrics:
        headline = ", ".join(f"{key}={value:.3f}" for key, value in list(metrics.items())[:3])
        metric_clause = f" A baseline model was evaluated ({headline})."
    return (
        f"Automated analysis covered a dataset of {rows} rows and {columns} columns, "
        f"yielding {len(insights)} documented finding(s).{metric_clause}"
    )


def _rule_based_advice(model_results: dict[str, Any] | None, evaluation_results: dict[str, Any] | None) -> str:
    if not model_results:
        return "No target column was configured; provide one to unlock baseline modeling and comparisons."
    name = model_results.get("model_name", "baseline model")
    if model_results.get("task") == "regression":
        r2 = (evaluation_results or {}).get("r2")
        quality = f"current R² is {r2:.3f}" if isinstance(r2, (int, float)) else "no R² was computed"
    else:
        f1 = (evaluation_results or {}).get("f1_macro")
        quality = f"macro F1 is {f1:.3f}" if isinstance(f1, (int, float)) else "no F1 was computed"
    return (
        f"The {name} is a single-estimator baseline and the {quality}; "
        "compare additional estimators and inspect feature importance before trusting it."
    )


def _parse_bullets(raw: str, limit: int) -> list[str]:
    """Extract clean findings from bullet/numbered/plain-line responses."""
    bullets: list[str] = []
    for chunk in raw.splitlines():
        line = re.sub(r"^(?:\s*[-*•]\s*|\s*\d+[.)]\s*)+", "", chunk.strip()).strip()
        if line:
            bullets.append(line)
        if len(bullets) >= limit:
            break
    return bullets


def _content(response: Any) -> str:
    content = getattr(response, "content", response)
    return content if isinstance(content, str) else str(content)


def _scalar_metrics(evaluation_results: dict[str, Any] | None) -> dict[str, float]:
    if not evaluation_results:
        return {}
    return {
        key: round(float(value), 4)
        for key, value in evaluation_results.items()
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    }


def _truncate(text: str, max_chars: int = _MAX_PROMPT_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + " …[truncated]"


__all__ = ["Narration", "advisor_note", "executive_summary", "narrate_insights"]
