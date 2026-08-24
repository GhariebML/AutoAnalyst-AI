"""Pure helpers powering the AutoAnalyst Streamlit dashboard.

Kept free of any Streamlit imports so the logic is unit-testable; the view
layer (``streamlit_app.py``) only renders what these functions produce.
"""

from __future__ import annotations

import json
import logging
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from autoanalyst.agents.prompts import ANSWER_PROMPT

logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB DoS guard for public deployments


def save_upload_to_temp(upload: Any, suffix: str = ".csv") -> str:
    """Persist an uploaded file to a temp path, enforcing the size cap."""
    data = upload.getvalue()
    if not data:
        raise ValueError("Uploaded file is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ValueError(f"File exceeds the {MAX_UPLOAD_BYTES // (1024 * 1024)} MB upload limit.")
    directory = Path(tempfile.gettempdir()) / "autoanalyst_uploads"
    directory.mkdir(exist_ok=True)
    path = directory / f"upload_{uuid.uuid4().hex}{suffix}"
    path.write_bytes(data)
    return str(path)


def trace_to_dataframe(trace: list[Any]) -> pd.DataFrame:
    """Render NodeRun records as a reviewable table."""
    rows = [
        {
            "node": entry.node,
            "status": entry.status,
            "duration_ms": entry.duration_ms,
            "attempts": entry.attempts,
            "error": entry.error or "",
        }
        for entry in trace
    ]
    return pd.DataFrame(rows, columns=["node", "status", "duration_ms", "attempts", "error"])


@dataclass
class RunContext:
    """Everything an analyst may ask about a completed run."""

    profile: dict[str, Any] = field(default_factory=dict)
    target_column: str | None = None
    model_results: dict[str, Any] | None = None
    evaluation_results: dict[str, Any] | None = None
    insights: list[str] = field(default_factory=list)
    executive_summary: str | None = None


def build_run_context(result: Any, target_column: str | None = None) -> RunContext:
    """Build a RunContext from a PipelineResult."""
    return RunContext(
        profile=dict(getattr(result, "profile", {}) or {}),
        target_column=target_column,
        model_results=getattr(result, "model_results", None),
        evaluation_results=getattr(result, "evaluation_results", None),
        insights=list(getattr(result, "insights", []) or []),
        executive_summary=getattr(result, "executive_summary", None),
    )


def answer_question(context: RunContext, question: str, llm: Any = None) -> str:
    """Answer analyst questions about the run; deterministic by default."""
    trimmed = (question or "").strip()
    if not trimmed:
        return "Ask about rows, columns, the target, metrics, insights, or the summary."
    if llm is not None:
        facts = {
            "profile": context.profile,
            "target_column": context.target_column,
            "model_results": context.model_results,
            "evaluation_metrics": scalar_metrics(context.evaluation_results),
            "insights": context.insights[:6],
            "executive_summary": context.executive_summary,
        }
        prompt = ANSWER_PROMPT.format(
            facts_json=json.dumps(facts, default=str)[:4000],
            question=trimmed,
        )
        try:
            content = getattr(llm.invoke(prompt), "content", "")
            text = content.strip() if isinstance(content, str) else str(content).strip()
            if text:
                return text
        except Exception as exc:
            logger.warning("LLM Q&A failed; using deterministic answers: %s", exc)

    lowered = lowered_text(trimmed, context)
    if any(word in lowered for word in ("row", "size", "how many records")):
        rows = context.profile.get("rows", "unknown")
        return f"The dataset contains {rows} rows."
    if "column" in lowered:
        names = context.profile.get("column_names")
        if names:
            shown = ", ".join(str(name) for name in names[:15])
            more = f" … (+{len(names) - 15} more)" if len(names) > 15 else ""
            return f"There are {context.profile.get('columns', '?')} columns: {shown}{more}."
        return f"The dataset has {context.profile.get('columns', '?')} columns."
    if any(word in lowered for word in ("target", "label")):
        if context.target_column:
            return f"The modeling target is '{context.target_column}'."
        return "No target column was configured for this run."
    if any(word in lowered for word in ("metric", "accuracy", "f1", "precision", "recall", "auc", "r2", "rmse")):
        metrics = scalar_metrics(context.evaluation_results)
        if metrics:
            formatted = ", ".join(f"{key}={value:.4f}" for key, value in metrics.items())
            return f"Evaluation metrics: {formatted}."
        return "No model evaluation is available for this run."
    if any(word in lowered for word in ("insight", "finding")):
        if context.insights:
            bullets = "\n".join(f"- {insight}" for insight in context.insights[:5])
            return f"Top findings:\n{bullets}"
        return "No insights were generated."
    if any(word in lowered for word in ("summary", "overview", "recap")):
        if context.executive_summary:
            return context.executive_summary
        return "No executive summary is available for this run."
    return (
        "I can answer questions about row/column counts, the target column, "
        "evaluation metrics, key findings, or the run summary."
    )


def lowered_text(question: str, context: RunContext) -> str:
    return question.lower()


def scalar_metrics(evaluation_results: dict[str, Any] | None) -> dict[str, float]:
    if not evaluation_results:
        return {}
    return {
        key: round(float(value), 4)
        for key, value in evaluation_results.items()
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    }


__all__ = [
    "MAX_UPLOAD_BYTES",
    "RunContext",
    "answer_question",
    "build_run_context",
    "save_upload_to_temp",
    "scalar_metrics",
    "trace_to_dataframe",
]
