"""LangChain-compatible tool wrappers for the Modeling Agent (Team 5).

Each function is decorated with ``@tool`` so it can be registered in a
LangChain ``AgentExecutor`` or called directly as a plain Python function
when the system runs in *deterministic mode* (no LLM required).

Tools
─────
train_classification_tool   — fit a classifier, return predictions & metadata
train_regression_tool       — fit a regressor, return predictions & metadata
train_clustering_tool       — fit a clusterer, return cluster assignments
compare_models_tool         — train multiple algorithms and rank them
get_feature_importances_tool— extract and rank feature importances
save_model_tool             — serialise a fitted estimator to disk
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_squared_error,
    r2_score,
    silhouette_score,
)
from sklearn.model_selection import train_test_split

from autoanalyst.modeling.classification import ClassificationModel
from autoanalyst.modeling.clustering import ClusteringModel
from autoanalyst.modeling.regression import RegressionModel

logger = logging.getLogger(__name__)

# ── Public constants ──────────────────────────────────────────────────────────
MODELS_DIR = Path(__file__).resolve().parents[4] / "models"
"""Default directory for serialised model files."""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ensure_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Raise a clear error if *df* still contains non-numeric columns."""
    bad_cols = list(df.select_dtypes(exclude=[np.number, bool, "bool", "boolean"]).columns)
    if bad_cols:
        raise ValueError(
            f"Features contain non-numeric columns: {bad_cols}. "
            "Apply encode_features() from the Preprocessing Agent first."
        )
    if df.isna().any().any():
        raise ValueError(
            "Features contain NaN values. "
            "Apply clean_data() from the Preprocessing Agent first."
        )
    return df


def _split(
    df: pd.DataFrame,
    target_col: str,
    test_size: float,
    random_state: int,
    stratify: bool,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Split *df* into train / test sets, returning X_train, X_test, y_train, y_test."""
    X = df.drop(columns=[target_col])
    y = df[target_col]
    _ensure_numeric(X)

    strat_arr = None
    if stratify:
        counts = y.value_counts()
        if (counts >= 2).all() and counts.nunique() >= 2:
            strat_arr = y
        else:
            logger.warning(
                "Stratification requested but not possible — "
                "some classes have fewer than 2 samples."
            )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=strat_arr,
    )
    return X_train, X_test, y_train, y_test


def _extract_importances(
    model_obj: Any, feature_names: list[str]
) -> dict[str, float]:
    """Return a {feature: importance} dict if the estimator supports it."""
    estimator = getattr(model_obj, "model", model_obj)
    if hasattr(estimator, "feature_importances_"):
        raw: np.ndarray = estimator.feature_importances_
        pairs = sorted(
            zip(feature_names, raw.tolist()),
            key=lambda x: x[1],
            reverse=True,
        )
        return {col: round(imp, 6) for col, imp in pairs}
    if hasattr(estimator, "coef_"):
        coefs = np.abs(estimator.coef_).flatten()
        if len(coefs) == len(feature_names):
            pairs = sorted(
                zip(feature_names, coefs.tolist()),
                key=lambda x: x[1],
                reverse=True,
            )
            return {col: round(imp, 6) for col, imp in pairs}
    return {}


# ── Classification tool ───────────────────────────────────────────────────────

def train_classification_tool(
    df: pd.DataFrame,
    target_column: str,
    algorithm: str = "random_forest",
    hyperparameters: dict[str, Any] | None = None,
    test_size: float = 0.2,
    random_state: int = 42,
    stratify: bool = False,
) -> dict[str, Any]:
    """Train a classification model and return structured results.

    Parameters
    ----------
    df:
        Cleaned, numeric-only DataFrame that includes the target column.
    target_column:
        Name of the binary or multi-class target column.
    algorithm:
        One of ``'random_forest'``, ``'logistic_regression'``,
        ``'svm'``, ``'decision_tree'``.
    hyperparameters:
        Optional dict of keyword arguments passed to the estimator.
    test_size:
        Fraction of data held out for testing.
    random_state:
        Random seed for reproducibility.
    stratify:
        Whether to perform stratified splitting.

    Returns
    -------
    dict
        JSON-serialisable result dict consumed by the Modeling Agent.
    """
    hp = hyperparameters or {}
    model = ClassificationModel(
        algorithm=algorithm,
        hyperparameters=hp,
        random_state=random_state,
    )

    X_train, X_test, y_train, y_test = _split(
        df, target_column, test_size, random_state, stratify
    )

    model.train(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = float(accuracy_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))
    importances = _extract_importances(model, list(X_train.columns))

    logger.info(
        "Classification training complete: algo=%s acc=%.4f f1=%.4f",
        algorithm, acc, f1,
    )

    return {
        "task_type": "classification",
        "algorithm_used": algorithm,
        "hyperparameters": hp,
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "accuracy": acc,
        "f1_weighted": f1,
        "predictions": y_pred.tolist(),
        "y_test": y_test.tolist(),
        "feature_importances": importances,
        "_model_object": model,  # internal — stripped before JSON export
    }


# ── Regression tool ───────────────────────────────────────────────────────────

def train_regression_tool(
    df: pd.DataFrame,
    target_column: str,
    algorithm: str = "random_forest",
    hyperparameters: dict[str, Any] | None = None,
    test_size: float = 0.2,
    random_state: int = 42,
) -> dict[str, Any]:
    """Train a regression model and return structured results.

    Parameters
    ----------
    df:
        Cleaned, numeric-only DataFrame that includes the target column.
    target_column:
        Name of the continuous numeric target column.
    algorithm:
        One of ``'random_forest'``, ``'linear_regression'``,
        ``'ridge'``, ``'lasso'``, ``'decision_tree'``.
    hyperparameters:
        Optional estimator keyword arguments.
    test_size:
        Test split fraction.
    random_state:
        Random seed.

    Returns
    -------
    dict
        JSON-serialisable result dict.
    """
    hp = hyperparameters or {}
    model = RegressionModel(
        algorithm=algorithm,
        hyperparameters=hp,
        random_state=random_state,
    )

    X_train, X_test, y_train, y_test = _split(
        df, target_column, test_size, random_state, stratify=False
    )

    model.train(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = float(mean_squared_error(y_test, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_test, y_pred))
    importances = _extract_importances(model, list(X_train.columns))

    logger.info(
        "Regression training complete: algo=%s rmse=%.4f r2=%.4f",
        algorithm, rmse, r2,
    )

    return {
        "task_type": "regression",
        "algorithm_used": algorithm,
        "hyperparameters": hp,
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "rmse": rmse,
        "r2": r2,
        "predictions": y_pred.tolist(),
        "y_test": y_test.tolist(),
        "feature_importances": importances,
        "_model_object": model,
    }


# ── Clustering tool ───────────────────────────────────────────────────────────

def train_clustering_tool(
    df: pd.DataFrame,
    algorithm: str = "kmeans",
    hyperparameters: dict[str, Any] | None = None,
    random_state: int = 42,
) -> dict[str, Any]:
    """Fit a clustering algorithm and return cluster assignments.

    Parameters
    ----------
    df:
        Cleaned, numeric-only feature DataFrame (no target column).
    algorithm:
        One of ``'kmeans'``, ``'dbscan'``, ``'agglomerative'``.
    hyperparameters:
        Optional estimator keyword arguments.
    random_state:
        Random seed (passed to KMeans / Agglomerative).

    Returns
    -------
    dict
        JSON-serialisable result dict.
    """
    _ensure_numeric(df)
    hp = hyperparameters or {}
    model = ClusteringModel(
        algorithm=algorithm,
        hyperparameters=hp,
        random_state=random_state,
    )

    labels: np.ndarray = model.train_predict(df)
    unique_labels = np.unique(labels)
    n_clusters = int(len(unique_labels[unique_labels != -1]))

    sil_score: float | None = None
    if n_clusters >= 2 and len(unique_labels) < len(df):
        try:
            sil_score = float(silhouette_score(df, labels))
        except Exception:
            pass

    logger.info(
        "Clustering complete: algo=%s n_clusters=%d silhouette=%s",
        algorithm, n_clusters, f"{sil_score:.4f}" if sil_score else "N/A",
    )

    return {
        "task_type": "clustering",
        "algorithm_used": algorithm,
        "hyperparameters": hp,
        "n_samples": int(len(df)),
        "n_clusters": n_clusters,
        "silhouette_score": sil_score,
        "cluster_assignments": labels.tolist(),
        "_model_object": model,
    }


# ── Model comparison tool ─────────────────────────────────────────────────────

def compare_models_tool(
    df: pd.DataFrame,
    target_column: str,
    task_type: str,
    algorithms: list[str],
    test_size: float = 0.2,
    random_state: int = 42,
    stratify: bool = False,
) -> list[dict[str, Any]]:
    """Train several algorithms on the same split and return a ranking table.

    Parameters
    ----------
    df:
        Cleaned, numeric-only DataFrame with target column.
    target_column:
        Target column name.
    task_type:
        ``'classification'`` or ``'regression'``.
    algorithms:
        List of algorithm identifiers to compare.
    test_size:
        Test split fraction.
    random_state:
        Random seed.
    stratify:
        Stratified split (classification only).

    Returns
    -------
    list[dict]
        Comparison table sorted by primary metric (accuracy ↓ / rmse ↑).
    """
    results: list[dict[str, Any]] = []

    for algo in algorithms:
        try:
            if task_type == "classification":
                res = train_classification_tool(
                    df, target_column, algo, None, test_size, random_state, stratify
                )
                results.append({
                    "algorithm": algo,
                    "accuracy": res["accuracy"],
                    "f1_weighted": res["f1_weighted"],
                    "train_rows": res["train_rows"],
                    "test_rows": res["test_rows"],
                })
            else:
                res = train_regression_tool(
                    df, target_column, algo, None, test_size, random_state
                )
                results.append({
                    "algorithm": algo,
                    "rmse": res["rmse"],
                    "r2": res["r2"],
                    "train_rows": res["train_rows"],
                    "test_rows": res["test_rows"],
                })
        except Exception as exc:
            logger.warning("Comparison: algo=%s failed: %s", algo, exc)
            results.append({"algorithm": algo, "error": str(exc)})

    # Sort by primary metric
    sort_key = "accuracy" if task_type == "classification" else "rmse"
    reverse = task_type == "classification"  # higher accuracy = better; lower rmse = better
    results.sort(
        key=lambda d: d.get(sort_key, float("inf") if not reverse else float("-inf")),
        reverse=reverse,
    )
    return results


# ── Feature importances tool ──────────────────────────────────────────────────

def get_feature_importances_tool(
    model_result: dict[str, Any],
    top_n: int = 10,
) -> list[dict[str, Any]]:
    """Extract and rank the top-N feature importances from a model result.

    Parameters
    ----------
    model_result:
        Dict returned by ``train_classification_tool`` or ``train_regression_tool``.
    top_n:
        Maximum number of features to return.

    Returns
    -------
    list[dict]
        List of ``{feature, importance}`` dicts sorted descending.
    """
    importances: dict[str, float] = model_result.get("feature_importances", {})
    ranked = sorted(importances.items(), key=lambda x: x[1], reverse=True)
    return [
        {"feature": feat, "importance": round(imp, 6)}
        for feat, imp in ranked[:top_n]
    ]


# ── Model persistence tool ────────────────────────────────────────────────────

def save_model_tool(
    model_result: dict[str, Any],
    filename: str | None = None,
    output_dir: str | Path | None = None,
) -> str:
    """Serialise the fitted estimator to a ``.joblib`` file.

    Parameters
    ----------
    model_result:
        Dict returned by one of the training tools — must contain
        ``'_model_object'`` (the wrapper instance).
    filename:
        Optional file name.  Auto-generated from algorithm name if omitted.
    output_dir:
        Directory for output.  Defaults to ``MODELS_DIR``.

    Returns
    -------
    str
        Absolute path of the saved file.
    """
    model_obj = model_result.get("_model_object")
    if model_obj is None:
        raise ValueError(
            "'_model_object' key not found in model_result.  "
            "Pass the raw tool output, not a JSON-serialised copy."
        )

    algo = model_result.get("algorithm_used", "model")
    out_dir = Path(output_dir) if output_dir else MODELS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    fname = filename or f"{algo}_estimator.joblib"
    if not fname.endswith(".joblib"):
        fname += ".joblib"
    out_path = out_dir / fname

    estimator = getattr(model_obj, "model", model_obj)
    joblib.dump(estimator, out_path)
    logger.info("Model saved → %s", out_path)
    return str(out_path)
