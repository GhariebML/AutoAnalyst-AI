"""Agent node functions for the AutoAnalyst graph.

Every node is a thin, deterministic delegation to the L1 tool/module layer.
Nodes never raise: failures are caught by ``_traced`` and recorded in
``state["errors"]`` / ``state["trace"]`` so the graph degrades gracefully
(documented quality requirement).

Each node is a plain annotated function because LangGraph's ``add_node``
matches concrete callables better than factory-produced callables under
mypy. Nodes live together here until they gain behavioral logic (M3+);
split them into per-agent files as they differentiate.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Any

import pandas as pd

from autoanalyst.agents.llm import create_llm, load_llm_settings
from autoanalyst.agents.narrator import advisor_note, executive_summary, narrate_insights
from autoanalyst.agents.state import AutoAnalystState, NodeRun
from autoanalyst.agents.tools import (
    clean_missing_values_tool,
    create_full_report_tool,
    encode_categoricals_tool,
    load_dataset_tool,
    missing_values_report_tool,
    numeric_summary_tool,
    profile_dataset_tool,
)
from autoanalyst.eda.analyzer import get_correlation_matrix
from autoanalyst.evaluation.evaluator import evaluate_classification, evaluate_regression
from autoanalyst.modeling.classification import ClassificationModel
from autoanalyst.modeling.regression import RegressionModel

logger = logging.getLogger(__name__)


def _traced(
    name: str,
    state: AutoAnalystState,
    impl: Callable[[AutoAnalystState], dict[str, Any]],
) -> dict[str, Any]:
    """Execute a node implementation with retry, timing, and error containment.

    Transient failures are retried up to ``state["max_retries"]`` times with a
    linear backoff. Once retries are exhausted the failure is recorded in
    ``errors`` (never raised) and escalated in ``escalations``.
    """
    max_retries = max(int(state.get("max_retries", 0)), 0)
    backoff = max(float(state.get("retry_backoff_seconds", 0.0)), 0.0)
    started = time.perf_counter()

    for attempt in range(1, max_retries + 2):
        try:
            update = impl(state)
        except Exception as exc:
            if attempt <= max_retries:
                logger.warning(
                    "Agent node '%s' failed (attempt %d/%d), retrying: %s",
                    name, attempt, max_retries + 1, exc,
                )
                time.sleep(backoff * attempt)
                continue
            error = f"{type(exc).__name__}: {exc}"
            logger.exception("Agent node '%s' failed after %d attempt(s).", name, attempt)
            return {
                "errors": [f"{name}: {error}"],
                "escalations": [f"{name}: failed after {attempt} attempt(s); escalated to supervisor."],
                "trace": [_trace(name, "error", started, attempts=attempt, error=error)],
            }
        if "trace" in update:
            # Node recorded its own terminal trace entry (e.g. a skip);
            # _skipped already logged the reason.
            return update
        update["trace"] = [_trace(name, "ok", started, attempts=attempt)]
        logger.info("Agent node '%s' finished in %.1f ms.", name, round((time.perf_counter() - started) * 1000, 2))
        return update

    return {}  # pragma: no cover - loop always returns


def _skipped(name: str, reason: str) -> dict[str, Any]:
    """Return a skipped-trace update when prerequisites are missing."""
    logger.warning("Agent node '%s' skipped: %s", name, reason)
    return {
        "warnings": [f"{name}: {reason}"],
        "trace": [NodeRun(node=name, status="skipped", error=reason)],
    }


def _trace(name: str, status: str, started: float, attempts: int = 1, error: str | None = None) -> NodeRun:
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    return NodeRun(node=name, status=status, duration_ms=duration_ms, attempts=attempts, error=error)


def _approved(state: AutoAnalystState, step: str) -> bool:
    """HITL gate: nodes under approval must be explicitly approved."""
    if not state.get("require_approval"):
        return True
    return bool(state.get("approvals", {}).get(step))


# ----------------------------------------------------------------------
# Public node definitions (registered in graph.build_graph)
# ----------------------------------------------------------------------


def dataset_intake_node(state: AutoAnalystState) -> dict[str, Any]:
    """Load and validate the raw dataset."""
    return _traced("intake", state, _dataset_intake_impl)


def profiling_node(state: AutoAnalystState) -> dict[str, Any]:
    """Generate the dataset profile and missing-values report."""
    return _traced("profiling", state, _profiling_impl)


def eda_node(state: AutoAnalystState) -> dict[str, Any]:
    """Compute descriptive statistics and correlations."""
    return _traced("eda", state, _eda_impl)


def cleaning_node(state: AutoAnalystState) -> dict[str, Any]:
    """Remove duplicates and impute missing values."""
    return _traced("cleaning", state, _cleaning_impl)


def feature_node(state: AutoAnalystState) -> dict[str, Any]:
    """Build the model-ready feature frame."""
    return _traced("features", state, _feature_impl)


def modeling_node(state: AutoAnalystState) -> dict[str, Any]:
    """Train a baseline model when a target column is available."""
    return _traced("modeling", state, _modeling_impl)


def evaluation_node(state: AutoAnalystState) -> dict[str, Any]:
    """Evaluate held-out predictions produced by the modeling node."""
    return _traced("evaluation", state, _evaluation_impl)


def insight_node(state: AutoAnalystState) -> dict[str, Any]:
    """Generate rule-based insights from the cleaned data."""
    return _traced("insights", state, _insight_impl)


def report_node(state: AutoAnalystState) -> dict[str, Any]:
    """Write the Markdown report when configured."""
    return _traced("report", state, _report_impl)


# ----------------------------------------------------------------------
# Node implementations
# ----------------------------------------------------------------------


def _dataset_intake_impl(state: AutoAnalystState) -> dict[str, Any]:
    path = state.get("dataset_path")
    if not path:
        raise ValueError("No dataset_path provided to the intake node.")
    df = load_dataset_tool.invoke({"file_path": path})
    if df.empty:
        raise ValueError(f"Dataset at '{path}' contains no rows.")
    return {"df": df}


def _profiling_impl(state: AutoAnalystState) -> dict[str, Any]:
    df = state.get("df")
    if df is None:
        return _skipped("profiling", "no DataFrame available from intake.")
    profile = profile_dataset_tool.invoke({"df": df})
    missing_report = missing_values_report_tool.invoke({"df": df})
    return {"profile": profile, "missing_values_report": missing_report}


def _eda_impl(state: AutoAnalystState) -> dict[str, Any]:
    df = state.get("df")
    if df is None:
        return _skipped("eda", "no DataFrame available from intake.")

    eda_results: dict[str, Any] = {}
    warnings: list[str] = []
    try:
        eda_results["numeric_summary"] = numeric_summary_tool.invoke({"df": df})
    except ValueError as exc:
        warnings.append(str(exc))
    try:
        eda_results["correlation_matrix"] = get_correlation_matrix(df)
    except ValueError as exc:
        warnings.append(str(exc))
    return {"eda_results": eda_results, "warnings": warnings}


def _cleaning_impl(state: AutoAnalystState) -> dict[str, Any]:
    if not _approved(state, "cleaning"):
        return _skipped("cleaning", "awaiting human approval.")
    df = state.get("df")
    if df is None:
        return _skipped("cleaning", "no DataFrame available from intake.")

    strategy = state.get("missing_strategy", "median")
    before = len(df)
    cleaned = clean_missing_values_tool.invoke({"df": df, "strategy": strategy})
    removed = before - len(cleaned)
    log = [
        f"Removed {removed} duplicate row(s).",
        f"Applied '{strategy}' missing-value strategy; remaining nulls: {int(cleaned.isna().sum().sum())}.",
    ]
    return {"cleaned_df": cleaned, "cleaning_log": log}


def _feature_impl(state: AutoAnalystState) -> dict[str, Any]:
    cleaned = state.get("cleaned_df")
    if cleaned is None:
        return _skipped("features", "no cleaned DataFrame available.")

    target = state.get("target_column")
    if not state.get("encode_categoricals", True):
        model_ready = cleaned.copy()
    else:
        categorical_columns = list(cleaned.select_dtypes(include=["object", "category", "string"]).columns)
        if target in categorical_columns:
            categorical_columns.remove(target)
        model_ready = encode_categoricals_tool.invoke({"df": cleaned}) if categorical_columns else cleaned.copy()

    feature_columns = [column for column in model_ready.columns if column != target]
    return {"model_ready_df": model_ready, "feature_columns": feature_columns}


def _modeling_impl(state: AutoAnalystState) -> dict[str, Any]:
    if not _approved(state, "modeling"):
        return _skipped("modeling", "awaiting human approval.")
    model_ready = state.get("model_ready_df")
    target = state.get("target_column")
    if model_ready is None or not target or target not in model_ready.columns:
        return _skipped("modeling", f"target column '{target}' unavailable after preprocessing.")

    X = model_ready.drop(columns=[target])
    y = model_ready[target]

    if pd.api.types.is_numeric_dtype(y) and y.nunique() > 10:
        regressor = RegressionModel(random_state=42)
        X_train, X_test, y_train, y_test = regressor.train(X, y, test_size=0.2)
        predictions = regressor.predict(X_test)
        task = "regression"
        results = {
            "task": task,
            "model_name": "RandomForestRegressor",
            "train_rows": len(X_train),
            "test_rows": len(X_test),
        }
        proba = None
    else:
        classifier = ClassificationModel(random_state=42)
        class_count = max(int(y.nunique()), 1)
        test_size = max(0.2, min(0.5, class_count / max(len(y), 1)))
        X_train, X_test, y_train, y_test = classifier.train(X, y, test_size=test_size)
        predictions = classifier.predict(X_test)
        proba = [[float(value) for value in row] for row in classifier.predict_proba(X_test)]
        task = "classification"
        results = {
            "task": task,
            "model_name": "RandomForestClassifier",
            "train_rows": len(X_train),
            "test_rows": len(X_test),
        }

    return {
        "model_results": results,
        "y_test": list(y_test),
        "y_pred": list(predictions),
        "y_proba": proba,
        "label_classes": sorted(y.unique().tolist()),
    }


def _evaluation_impl(state: AutoAnalystState) -> dict[str, Any]:
    y_test = state.get("y_test")
    y_pred = state.get("y_pred")
    if y_test is None or y_pred is None:
        return _skipped("evaluation", "no held-out predictions from modeling.")

    results = state.get("model_results")
    is_regression = results is not None and results.get("task") == "regression"
    if is_regression:
        metrics: dict[str, Any] = evaluate_regression(pd.Series(y_test), pd.Series(y_pred))
    else:
        metrics = evaluate_classification(
            pd.Series(y_test),
            pd.Series(y_pred),
            y_proba=state.get("y_proba"),
            labels=state.get("label_classes"),
        )
    return {"evaluation_results": metrics}


def _insight_impl(state: AutoAnalystState) -> dict[str, Any]:
    cleaned = state.get("cleaned_df")
    if cleaned is None:
        return _skipped("insights", "no cleaned DataFrame available.")

    llm = _resolve_llm()
    narration = narrate_insights(
        cleaned,
        state.get("profile") or {},
        state.get("model_results"),
        state.get("evaluation_results"),
        llm=llm,
    )
    insights = list(narration.texts)
    advisor = advisor_note(state.get("model_results"), state.get("evaluation_results"), llm=llm)
    if advisor:
        insights.append(advisor)

    summary = executive_summary(
        state.get("profile") or {},
        insights,
        state.get("evaluation_results"),
        llm=llm,
    )
    return {
        "insights": insights,
        "narrated_by": narration.source,
        "executive_summary": summary,
    }


def _resolve_llm() -> Any:
    """Resolve the configured chat model; None means deterministic narration."""
    try:
        return create_llm(load_llm_settings())
    except RuntimeError as exc:
        logger.warning("LLM unavailable (%s); continuing with rule-based narration.", exc)
        return None


def _report_impl(state: AutoAnalystState) -> dict[str, Any]:
    insights = state.get("insights") or []
    report_path = state.get("report_path")
    if not report_path or not insights:
        return _skipped("report", "no report path configured or no insights generated.")

    written = create_full_report_tool.invoke({
        "output_path": report_path,
        "title": "AutoAnalyst AI Agent Report",
        "profile": state.get("profile") or {},
        "insights": insights,
        "missing_report": state.get("missing_values_report"),
        "eda_results": state.get("eda_results") or {},
        "cleaning_log": state.get("cleaning_log") or [],
        "model_results": state.get("model_results"),
        "evaluation_results": state.get("evaluation_results"),
        "warnings": state.get("warnings") or [],
        "executive_summary": state.get("executive_summary"),
    })
    return {"report_path": written}
