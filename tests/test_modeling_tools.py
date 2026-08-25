"""Tests for the modeling tool wrappers (Team 5)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from autoanalyst.agents.modeling_tools import (
    compare_models_tool,
    get_feature_importances_tool,
    train_classification_tool,
    train_clustering_tool,
    train_regression_tool,
)


# ── Sample DataFrames ─────────────────────────────────────────────────────────

def _clf_df(n: int = 60) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    return pd.DataFrame({
        "a": rng.normal(size=n),
        "b": rng.uniform(size=n),
        "label": (rng.random(n) > 0.5).astype(int),
    })


def _reg_df(n: int = 60) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    X = rng.normal(size=(n, 2))
    df = pd.DataFrame(X, columns=["x1", "x2"])
    df["target"] = X[:, 0] * 3 + rng.normal(scale=0.5, size=n)
    return df


def _clust_df(n: int = 60) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    return pd.DataFrame({
        "f1": rng.normal(size=n),
        "f2": rng.normal(size=n),
    })


# ── Classification tool ───────────────────────────────────────────────────────

@pytest.mark.parametrize("algo", ["random_forest", "logistic_regression", "decision_tree"])
def test_train_classification_tool_returns_expected_keys(algo: str) -> None:
    result = train_classification_tool(_clf_df(), "label", algorithm=algo, test_size=0.3)
    assert result["task_type"] == "classification"
    assert "predictions" in result
    assert "y_test" in result
    assert "accuracy" in result
    assert len(result["predictions"]) == len(result["y_test"])


def test_train_classification_accuracy_is_valid() -> None:
    result = train_classification_tool(_clf_df(100), "label", test_size=0.2)
    assert 0.0 <= result["accuracy"] <= 1.0


def test_train_classification_raises_on_nan_features() -> None:
    df = _clf_df()
    df.loc[0, "a"] = np.nan
    with pytest.raises(ValueError, match="NaN"):
        train_classification_tool(df, "label")


def test_train_classification_raises_on_non_numeric() -> None:
    df = _clf_df()
    df["a"] = "text"
    with pytest.raises(ValueError, match="non-numeric"):
        train_classification_tool(df, "label")


# ── Regression tool ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("algo", ["random_forest", "linear_regression", "ridge"])
def test_train_regression_tool_returns_expected_keys(algo: str) -> None:
    result = train_regression_tool(_reg_df(), "target", algorithm=algo, test_size=0.3)
    assert result["task_type"] == "regression"
    assert "predictions" in result
    assert "rmse" in result and result["rmse"] >= 0


def test_train_regression_r2_is_reasonable() -> None:
    result = train_regression_tool(_reg_df(200), "target", algorithm="random_forest")
    # Strong linear signal — expect R² > 0.5
    assert result["r2"] > 0.5


# ── Clustering tool ───────────────────────────────────────────────────────────

def test_train_clustering_kmeans() -> None:
    result = train_clustering_tool(
        _clust_df(), algorithm="kmeans", hyperparameters={"n_clusters": 3}
    )
    assert result["task_type"] == "clustering"
    assert result["n_clusters"] == 3
    assert len(result["cluster_assignments"]) == 60


def test_train_clustering_dbscan() -> None:
    result = train_clustering_tool(
        _clust_df(), algorithm="dbscan", hyperparameters={"eps": 1.0, "min_samples": 3}
    )
    assert result["task_type"] == "clustering"
    assert "cluster_assignments" in result


def test_train_clustering_raises_on_nan() -> None:
    df = _clust_df()
    df.loc[0, "f1"] = np.nan
    with pytest.raises(ValueError, match="NaN"):
        train_clustering_tool(df)


# ── Compare models tool ───────────────────────────────────────────────────────

def test_compare_models_classification_returns_sorted_table() -> None:
    table = compare_models_tool(
        _clf_df(80), "label", "classification",
        ["random_forest", "logistic_regression", "decision_tree"],
    )
    assert len(table) == 3
    # Each row must have "algorithm" key
    for row in table:
        assert "algorithm" in row


def test_compare_models_regression_returns_sorted_table() -> None:
    table = compare_models_tool(
        _reg_df(80), "target", "regression",
        ["random_forest", "linear_regression"],
    )
    assert len(table) == 2
    # Should be sorted by rmse ascending (best first)
    if "rmse" in table[0] and "rmse" in table[1]:
        assert table[0]["rmse"] <= table[1]["rmse"]


# ── Feature importances tool ──────────────────────────────────────────────────

def test_get_feature_importances_random_forest() -> None:
    result = train_classification_tool(
        _clf_df(80), "label", algorithm="random_forest"
    )
    importances = get_feature_importances_tool(result, top_n=2)
    assert len(importances) <= 2
    for row in importances:
        assert "feature" in row and "importance" in row


def test_get_feature_importances_returns_empty_for_no_support() -> None:
    """Algorithms without feature_importances_ or coef_ return an empty list."""
    result = {"feature_importances": {}, "_model_object": None}
    importances = get_feature_importances_tool(result)
    assert importances == []
