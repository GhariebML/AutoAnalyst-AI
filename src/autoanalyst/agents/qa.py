"""Chat Q&A over a completed run: LLM-enriched answers with rule fallbacks.

Follows the narration contract (see ``agents/narrator.py``):
- pass ``llm=None`` and questions are answered from deterministic fact
  extraction with zero model calls
- pass a chat model (real or a test double) for natural-language answers
- any LLM failure degrades to the deterministic fallback, never an exception
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel

from autoanalyst.agents.prompts import ANSWER_PROMPT
from autoanalyst.pipeline import PipelineResult

logger = logging.getLogger(__name__)

_MAX_PROMPT_CHARS = 4000

_METRIC_ALIASES: dict[str, tuple[str, ...]] = {
    "accuracy": ("accuracy", "accurate"),
    "f1": ("f1",),
    "precision": ("precision",),
    "recall": ("recall",),
    "r2": ("r2", "r²"),
    "rmse": ("rmse",),
    "mae": ("mae",),
}


@dataclass
class Answer:
    """Produced answer plus its provenance."""

    text: str
    source: str = "rules"  # "rules" | "llm"


def build_facts(result: PipelineResult) -> dict[str, Any]:
    """Condense a PipelineResult into the compact JSON facts used by Q&A."""
    facts: dict[str, Any] = {
        "rows": int(result.raw_df.shape[0]),
        "columns": int(result.raw_df.shape[1]),
        "column_names": [str(column) for column in result.raw_df.columns],
        "missing_values": int(result.raw_df.isna().sum().sum()),
        "cleaned_rows": int(result.cleaned_df.shape[0]),
    }
    profile_metrics = {
        key: value
        for key, value in (result.profile or {}).items()
        if isinstance(value, (int, float, str)) and not isinstance(value, bool)
    }
    if profile_metrics:
        facts["profile"] = profile_metrics
    if result.model_results:
        facts["model"] = {
            key: value
            for key, value in result.model_results.items()
            if isinstance(value, (int, float, str)) and not isinstance(value, bool)
        }
    scalar_metrics = _scalar_metrics(result.evaluation_results)
    if scalar_metrics:
        facts["metrics"] = scalar_metrics
    if result.insights:
        facts["insights"] = list(result.insights[:8])
    if result.warnings:
        facts["warnings"] = list(result.warnings[:5])
    return facts


def answer_question(
    result: PipelineResult,
    question: str,
    *,
    llm: BaseChatModel | None = None,
) -> Answer:
    """Answer a question about a completed run; rules fallback without an LLM."""
    facts = build_facts(result)
    question = (question or "").strip()
    if not question:
        return Answer(
            text="Ask me about the dataset shape, missing values, model metrics, or insights.",
            source="rules",
        )

    if llm is not None:
        prompt = ANSWER_PROMPT.format(
            facts_json=_truncate(json.dumps(facts, default=str)),
            question=question,
        )
        try:
            text = _content(llm.invoke(prompt)).strip()
            if text:
                return Answer(text=text, source="llm")
        except Exception as exc:
            logger.warning("LLM Q&A failed; using deterministic answer: %s", exc)

    return Answer(text=_rule_based_answer(facts, question), source="rules")


def _rule_based_answer(facts: dict[str, Any], question: str) -> str:
    lowered = question.lower()

    metric_hits = [
        name
        for name, aliases in _METRIC_ALIASES.items()
        if any(alias in lowered for alias in aliases) and name in facts.get("metrics", {})
    ]
    if metric_hits:
        metrics = facts["metrics"]
        rendered = ", ".join(f"{name}={metrics[name]:.3f}" for name in metric_hits[:4])
        model_name = facts.get("model", {}).get("model_name")
        clause = f" for the {model_name}" if model_name else ""
        return f"{rendered}{clause}."

    if any(word in lowered for word in ("row", "column", "shape", "size", "big", "dimension")):
        return (
            f"The dataset has {facts['rows']} rows and {facts['columns']} columns; "
            f"after cleaning it holds {facts['cleaned_rows']} rows."
        )

    if "missing" in lowered or "nan" in lowered or "null" in lowered:
        return f"The raw dataset contains {facts['missing_values']} missing value(s)."

    if "model" in lowered or "algorithm" in lowered or "trained" in lowered:
        model = facts.get("model")
        if not model:
            return "No model was trained because no target column was configured."
        task = model.get("task", "unknown task")
        return f"A {model.get('model_name', 'baseline model')} was trained for {task}."

    if "insight" in lowered or "finding" in lowered:
        insights = facts.get("insights") or []
        if not insights:
            return "No insights were recorded for this run."
        bullets = "\n".join(f"- {insight}" for insight in insights[:3])
        more = f"\n(+{len(insights) - 3} more)" if len(insights) > 3 else ""
        return f"Top findings:\n{bullets}{more}"

    if "warning" in lowered or "problem" in lowered or "issue" in lowered:
        warnings = facts.get("warnings") or []
        if not warnings:
            return "The run completed without pipeline warnings."
        bullets = "\n".join(f"- {warning}" for warning in warnings[:3])
        return f"Pipeline warnings:\n{bullets}"

    topics = sorted({"shape", "missing values", "model", "metrics", "insights", "warnings"} & set(_topic_keys(facts)))
    available = ", ".join(topics)
    return (
        "I can only answer from this run's facts. Ask about "
        f"{available or 'the dataset'} — or provide the data needed for anything else."
    )


def _topic_keys(facts: dict[str, Any]) -> list[str]:
    keys = ["shape"]
    if facts.get("missing_values") is not None:
        keys.append("missing values")
    if facts.get("model"):
        keys.append("model")
    if facts.get("metrics"):
        keys.append("metrics")
    if facts.get("insights"):
        keys.append("insights")
    if facts.get("warnings"):
        keys.append("warnings")
    return keys


def _scalar_metrics(evaluation_results: dict[str, Any] | None) -> dict[str, float]:
    if not evaluation_results:
        return {}
    return {
        key: round(float(value), 4)
        for key, value in evaluation_results.items()
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    }


def _content(response: Any) -> str:
    content = getattr(response, "content", response)
    return content if isinstance(content, str) else str(content)


def _truncate(text: str, max_chars: int = _MAX_PROMPT_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + " …[truncated]"


__all__ = ["Answer", "answer_question", "build_facts"]
