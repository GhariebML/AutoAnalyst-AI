"""End-to-end tests for the Modeling Agent node (Team 5)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from autoanalyst.agents.modeling_agent import modeling_node
from autoanalyst.agents.state import AutoAnalystState


# ── Dataset factories ─────────────────────────────────────────────────────────

def _make_classification_state(n: int = 80) -> AutoAnalystState:
    rng = np.random.default_rng(42)
    df = pd.DataFrame({
        "age": rng.integers(20, 65, size=n).astype(float),
        "income": rng.uniform(30_000, 120_000, size=n),
        "score": rng.normal(50, 10, size=n),
        "promoted": (rng.random(n) > 0.5).astype(int),
    })
    return AutoAnalystState(
        cleaned_df=df,
        target_column="promoted",
        errors=[],
        warnings=[],
    )


def _make_regression_state(n: int = 80) -> AutoAnalystState:
    rng = np.random.default_rng(0)
    X = rng.normal(size=(n, 3))
    df = pd.DataFrame(X, columns=["x1", "x2", "x3"])
    df["salary"] = X[:, 0] * 5000 + 60_000 + rng.normal(scale=500, size=n)
    return AutoAnalystState(
        cleaned_df=df,
        target_column="salary",
        errors=[],
        warnings=[],
    )


def _make_clustering_state(n: int = 60) -> AutoAnalystState:
    rng = np.random.default_rng(7)
    df = pd.DataFrame({
        "lat": rng.normal(size=n),
        "lon": rng.normal(size=n),
        "elevation": rng.uniform(size=n),
    })
    return AutoAnalystState(
        cleaned_df=df,
        target_column=None,
        errors=[],
        warnings=[],
    )


# ── Classification agent tests ────────────────────────────────────────────────

def test_modeling_node_classification_populates_model_results() -> None:
    state = _make_classification_state()
    result = modeling_node(state)

    assert "model_results" in result
    mr = result["model_results"]
    assert mr is not None
    assert mr["task_type"] == "classification"
    assert "algorithm_used" in mr
    assert "predictions" in mr
    assert "y_test" in mr
    assert 0.0 <= mr["accuracy"] <= 1.0


def test_modeling_node_classification_no_errors() -> None:
    state = _make_classification_state()
    result = modeling_node(state)
    assert result["errors"] == []


def test_modeling_node_classification_has_decision_log() -> None:
    state = _make_classification_state()
    result = modeling_node(state)
    assert len(result["model_results"]["decision_log"]) >= 1


def test_modeling_node_classification_has_comparison() -> None:
    state = _make_classification_state()
    result = modeling_node(state)
    comparison = result["model_results"].get("comparison", [])
    assert len(comparison) >= 1


def test_modeling_node_no_internal_model_object_in_state() -> None:
    """The _model_object key must never leak into the state."""
    state = _make_classification_state()
    result = modeling_node(state)
    mr = result["model_results"]
    assert "_model_object" not in mr


# ── Regression agent tests ────────────────────────────────────────────────────

def test_modeling_node_regression_populates_model_results() -> None:
    state = _make_regression_state()
    result = modeling_node(state)

    mr = result["model_results"]
    assert mr is not None
    assert mr["task_type"] == "regression"
    assert mr["rmse"] >= 0


def test_modeling_node_regression_no_errors() -> None:
    state = _make_regression_state()
    result = modeling_node(state)
    assert result["errors"] == []


# ── Clustering agent tests ────────────────────────────────────────────────────

def test_modeling_node_clustering_populates_model_results() -> None:
    state = _make_clustering_state()
    result = modeling_node(state)

    mr = result["model_results"]
    assert mr is not None
    assert mr["task_type"] == "clustering"
    assert "cluster_assignments" in mr
    assert mr["n_clusters"] >= 2


def test_modeling_node_clustering_no_errors() -> None:
    state = _make_clustering_state()
    result = modeling_node(state)
    assert result["errors"] == []


# ── Graceful degradation tests ────────────────────────────────────────────────

def test_modeling_node_falls_back_to_raw_df_when_no_cleaned_df() -> None:
    """If cleaned_df is absent, the agent should use df and add a warning."""
    rng = np.random.default_rng(1)
    raw_df = pd.DataFrame({
        "a": rng.normal(size=40),
        "b": rng.normal(size=40),
        "label": (rng.random(40) > 0.5).astype(int),
    })
    state = AutoAnalystState(
        df=raw_df,
        target_column="label",
        errors=[],
        warnings=[],
    )
    result = modeling_node(state)
    assert result["model_results"] is not None
    assert any("falling back" in w.lower() for w in result["warnings"])


def test_modeling_node_records_error_when_no_df() -> None:
    """With no DataFrame at all, errors list must be populated and no crash."""
    state = AutoAnalystState(target_column="label", errors=[], warnings=[])
    result = modeling_node(state)
    assert result.get("model_results") is None
    assert len(result["errors"]) >= 1


def test_modeling_node_preserves_existing_state_keys() -> None:
    """The node must merge with existing state, not overwrite unrelated keys."""
    state = _make_classification_state()
    state["profile"] = {"rows": 80, "columns": 4}
    state["insights"] = ["Dataset has 80 rows."]
    result = modeling_node(state)
    assert result.get("profile") == {"rows": 80, "columns": 4}
    assert result.get("insights") == ["Dataset has 80 rows."]
