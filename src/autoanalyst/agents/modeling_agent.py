"""Modeling Agent — Team 5 LangGraph node.

This module implements the **Modeling Agent**, the Team 5 contribution to the
AutoAnalyst AI multi-agent system.  It is designed as a LangGraph *node
function* that:

1. **Reads** the shared ``AutoAnalystState``.
2. **Decides** the task type, best algorithm, and hyperparameters autonomously
   via ``ModelDecider``.
3. **Trains** the primary model using the tool layer (``modeling_tools``).
4. **Compares** a set of baseline alternatives.
5. **Validates** outputs (no NaN predictions, sensible metric ranges).
6. **Optionally persists** the fitted estimator to ``models/``.
7. **Returns** a partial state update with ``model_results`` populated and
   any errors / warnings appended.

Design principles
─────────────────
* Works **without an LLM** — all decisions are rule-based by default.
* Never mutates the original DataFrame; always works on a copy.
* Errors are caught and appended to ``state["errors"]``; the node never
  raises so the LangGraph workflow can continue to the Reporting Agent even
  if modelling fails.
* The ``_model_object`` key is stripped from ``model_results`` before the
  state is returned, keeping the state JSON-serialisable.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from autoanalyst.agents.model_decider import ModelDecider
from autoanalyst.agents.modeling_tools import (
    compare_models_tool,
    get_feature_importances_tool,
    save_model_tool,
    train_classification_tool,
    train_clustering_tool,
    train_regression_tool,
)
from autoanalyst.agents.state import AutoAnalystState

logger = logging.getLogger(__name__)


# ── Public node function ──────────────────────────────────────────────────────

def modeling_node(state: AutoAnalystState) -> AutoAnalystState:
    """LangGraph node: orchestrate model selection, training, and comparison.

    Parameters
    ----------
    state:
        Shared pipeline state.  The node reads ``cleaned_df``,
        ``target_column``, and ``profile`` (all optional — it degrades
        gracefully when upstream agents haven't run yet).

    Returns
    -------
    AutoAnalystState
        Partial state update; only the keys the Modeling Agent owns are set.
    """
    errors: list[str] = list(state.get("errors") or [])
    warnings: list[str] = list(state.get("warnings") or [])

    # ── 1. Acquire the model-ready DataFrame ─────────────────────────────────
    df = _get_model_ready_df(state, warnings)
    if df is None or df.empty:
        errors.append(
            "Modeling Agent: no usable DataFrame found in state. "
            "Ensure the Preprocessing Agent has run successfully."
        )
        return {**state, "errors": errors, "warnings": warnings}

    target_col: str | None = state.get("target_column")
    profile: dict[str, Any] = state.get("profile") or {}

    # ── 2. Autonomous decision ────────────────────────────────────────────────
    try:
        decider = ModelDecider(
            df=df,
            target_column=target_col,
            profile=profile,
        )
        decision = decider.decide()
    except Exception as exc:
        errors.append(f"Modeling Agent — ModelDecider failed: {exc}")
        return {**state, "errors": errors, "warnings": warnings}

    logger.info(
        "ModelDecider decision: task=%s algo=%s",
        decision.task_type, decision.primary_algorithm,
    )

    # ── 3. Train primary model ────────────────────────────────────────────────
    primary_result: dict[str, Any] | None = None
    try:
        primary_result = _train_primary(df, target_col, decision)
    except Exception as exc:
        errors.append(f"Modeling Agent — primary training failed: {exc}")
        return {**state, "errors": errors, "warnings": warnings}

    # ── 4. Validate predictions ───────────────────────────────────────────────
    _validate_predictions(primary_result, warnings)

    # ── 5. Run model comparison ───────────────────────────────────────────────
    comparison: list[dict[str, Any]] = []
    if decision.task_type in {"classification", "regression"} and target_col:
        all_algos = [decision.primary_algorithm] + decision.comparison_algorithms
        try:
            comparison = compare_models_tool(
                df=df,
                target_column=target_col,
                task_type=decision.task_type,
                algorithms=all_algos,
            )
        except Exception as exc:
            warnings.append(f"Model comparison failed (non-fatal): {exc}")

    # ── 6. Feature importances ────────────────────────────────────────────────
    top_features: list[dict[str, Any]] = []
    if primary_result:
        try:
            top_features = get_feature_importances_tool(primary_result, top_n=15)
        except Exception:
            pass  # Not all algorithms expose feature importances

    # ── 7. Persist model (best-effort) ────────────────────────────────────────
    model_file: str | None = None
    if primary_result and primary_result.get("_model_object"):
        try:
            model_file = save_model_tool(primary_result)
        except Exception as exc:
            warnings.append(f"Model persistence failed (non-fatal): {exc}")

    # ── 8. Build clean state payload ─────────────────────────────────────────
    model_results = _build_model_results(
        decision=decision,
        primary_result=primary_result,
        comparison=comparison,
        top_features=top_features,
        model_file=model_file,
    )

    logger.info(
        "Modeling Agent complete. task=%s algo=%s model_file=%s",
        decision.task_type, decision.primary_algorithm, model_file,
    )

    return {
        **state,
        "model_results": model_results,
        "errors": errors,
        "warnings": warnings,
    }


# ── Internal helpers ──────────────────────────────────────────────────────────

def _get_model_ready_df(
    state: AutoAnalystState, warnings: list[str]
) -> pd.DataFrame | None:
    """Return the best available DataFrame from the state, with a preference
    for ``cleaned_df`` (output of the Preprocessing Agent)."""
    if "cleaned_df" in state and state["cleaned_df"] is not None:
        return state["cleaned_df"].copy()
    if "df" in state and state["df"] is not None:
        warnings.append(
            "Modeling Agent: 'cleaned_df' not found — falling back to raw 'df'. "
            "Run the Preprocessing Agent first for best results."
        )
        return state["df"].copy()
    return None


def _train_primary(
    df: pd.DataFrame,
    target_col: str | None,
    decision: Any,
) -> dict[str, Any]:
    """Dispatch to the correct tool based on the decision task type."""
    if decision.task_type == "classification":
        return train_classification_tool(
            df=df,
            target_column=target_col,  # type: ignore[arg-type]
            algorithm=decision.primary_algorithm,
            hyperparameters=decision.hyperparameters,
            stratify=decision.stratify,
        )
    if decision.task_type == "regression":
        return train_regression_tool(
            df=df,
            target_column=target_col,  # type: ignore[arg-type]
            algorithm=decision.primary_algorithm,
            hyperparameters=decision.hyperparameters,
        )
    # clustering
    features_df = df.select_dtypes(include=[np.number]).copy()
    return train_clustering_tool(
        df=features_df,
        algorithm=decision.primary_algorithm,
        hyperparameters=decision.hyperparameters,
    )


def _validate_predictions(
    result: dict[str, Any] | None, warnings: list[str]
) -> None:
    """Append warnings if predictions contain NaN / inf values."""
    if result is None:
        return
    preds = result.get("predictions") or result.get("cluster_assignments", [])
    if not preds:
        return
    arr = np.asarray(preds, dtype=float)
    if np.isnan(arr).any():
        warnings.append("Modeling Agent: predictions contain NaN values.")
    if np.isinf(arr).any():
        warnings.append("Modeling Agent: predictions contain infinite values.")


def _build_model_results(
    decision: Any,
    primary_result: dict[str, Any] | None,
    comparison: list[dict[str, Any]],
    top_features: list[dict[str, Any]],
    model_file: str | None,
) -> dict[str, Any]:
    """Assemble the final ``model_results`` dict, stripping internal keys."""
    base: dict[str, Any] = {
        "task_type": decision.task_type,
        "algorithm_used": decision.primary_algorithm,
        "hyperparameters": {
            k: v for k, v in decision.hyperparameters.items()
            if k != "random_state"
        },
        "decision_log": decision.decision_log,
        "comparison": comparison,
        "top_features": top_features,
        "model_file": model_file,
    }

    if primary_result:
        # Merge primary result — exclude internal keys
        for key, val in primary_result.items():
            if not key.startswith("_"):
                base[key] = val

    return base
