"""Tests for ModelDecider — autonomous task/algorithm selection logic."""

from __future__ import annotations

import pandas as pd
import pytest

from autoanalyst.agents.model_decider import ModelDecider


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _classification_df(n: int = 100) -> pd.DataFrame:
    """Numeric features + binary categorical target."""
    import numpy as np
    rng = np.random.default_rng(42)
    return pd.DataFrame({
        "feat_a": rng.normal(size=n),
        "feat_b": rng.uniform(size=n),
        "label": (rng.random(n) > 0.5).astype(int),
    })


def _regression_df(n: int = 100) -> pd.DataFrame:
    """Numeric features + continuous numeric target."""
    import numpy as np
    rng = np.random.default_rng(0)
    X = rng.normal(size=(n, 3))
    y = X[:, 0] * 2.5 + rng.normal(scale=0.1, size=n)
    df = pd.DataFrame(X, columns=["a", "b", "c"])
    df["price"] = y
    return df


def _clustering_df(n: int = 100) -> pd.DataFrame:
    """Numeric-only DataFrame (no target column)."""
    import numpy as np
    rng = np.random.default_rng(7)
    return pd.DataFrame({
        "x": rng.normal(size=n),
        "y": rng.normal(size=n),
    })


# ── Task detection tests ───────────────────────────────────────────────────────

def test_detects_classification_binary() -> None:
    df = _classification_df()
    result = ModelDecider(df, target_column="label").decide()
    assert result.task_type == "classification"


def test_detects_classification_categorical_target() -> None:
    import numpy as np
    df = pd.DataFrame({
        "a": np.random.normal(size=50),
        "b": np.random.normal(size=50),
        "cat": (["yes", "no"] * 25),
    })
    result = ModelDecider(df, target_column="cat").decide()
    assert result.task_type == "classification"


def test_detects_regression() -> None:
    df = _regression_df(n=200)
    # "price" has many unique values — should be regression
    result = ModelDecider(df, target_column="price").decide()
    assert result.task_type == "regression"


def test_detects_clustering_no_target() -> None:
    df = _clustering_df()
    result = ModelDecider(df, target_column=None).decide()
    assert result.task_type == "clustering"


def test_detects_clustering_missing_target_column() -> None:
    df = _clustering_df()
    result = ModelDecider(df, target_column="nonexistent_col").decide()
    assert result.task_type == "clustering"


# ── Algorithm selection tests ──────────────────────────────────────────────────

def test_small_classification_prefers_logistic() -> None:
    df = _classification_df(n=50)
    result = ModelDecider(df, target_column="label").decide()
    assert result.primary_algorithm == "logistic_regression"


def test_large_classification_prefers_random_forest() -> None:
    df = _classification_df(n=500)
    result = ModelDecider(df, target_column="label").decide()
    assert result.primary_algorithm == "random_forest"


def test_small_regression_prefers_linear() -> None:
    df = _regression_df(n=50)
    result = ModelDecider(df, target_column="price").decide()
    assert result.primary_algorithm == "linear_regression"


def test_large_regression_prefers_random_forest() -> None:
    df = _regression_df(n=500)
    result = ModelDecider(df, target_column="price").decide()
    assert result.primary_algorithm == "random_forest"


def test_clustering_uses_kmeans_by_default() -> None:
    df = _clustering_df()
    result = ModelDecider(df, target_column=None).decide()
    assert result.primary_algorithm == "kmeans"
    assert "n_clusters" in result.hyperparameters


# ── Decision log ──────────────────────────────────────────────────────────────

def test_decision_log_is_populated() -> None:
    df = _classification_df()
    result = ModelDecider(df, target_column="label").decide()
    assert len(result.decision_log) >= 2


# ── Stratify ─────────────────────────────────────────────────────────────────

def test_stratify_enabled_for_balanced_classes() -> None:
    import numpy as np
    n = 100  # Large enough → random_forest is chosen, all classes have ≥50 samples
    df = pd.DataFrame({
        "a": np.ones(n),
        "b": np.zeros(n),
        "label": [0] * (n // 2) + [1] * (n // 2),
    })
    result = ModelDecider(df, target_column="label").decide()
    assert result.stratify is True


def test_stratify_disabled_for_rare_class() -> None:
    import numpy as np
    # Only 1 sample in minority class
    df = pd.DataFrame({
        "a": np.ones(10),
        "label": [0] * 9 + [1],
    })
    result = ModelDecider(df, target_column="label").decide()
    assert result.stratify is False
