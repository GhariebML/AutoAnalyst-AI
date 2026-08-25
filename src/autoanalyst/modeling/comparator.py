"""Multi-model comparison utility — Team 5."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from autoanalyst.modeling.classification import ClassificationModel
from autoanalyst.modeling.regression import RegressionModel
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error, r2_score
import numpy as np

logger = logging.getLogger(__name__)


def compare_classification_models(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    algorithms: list[str] | None = None,
    random_state: int = 42,
) -> list[dict[str, Any]]:
    """Train multiple classifiers on the same split and return a ranking table.

    Parameters
    ----------
    X_train, X_test, y_train, y_test:
        Pre-split data (avoids data-leakage between comparison runs).
    algorithms:
        List of algorithm names to compare.  Defaults to all four
        supported classifiers.
    random_state:
        Passed to each model.

    Returns
    -------
    list[dict]
        Rows sorted by ``f1_weighted`` descending.
    """
    algos = algorithms or ["random_forest", "logistic_regression", "decision_tree"]
    rows: list[dict[str, Any]] = []

    for algo in algos:
        try:
            model = ClassificationModel(algorithm=algo, random_state=random_state)
            model.train(X_train, y_train)
            y_pred = model.predict(X_test)
            rows.append({
                "algorithm": algo,
                "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
                "f1_weighted": round(float(f1_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
                "train_rows": int(len(X_train)),
                "test_rows": int(len(X_test)),
            })
            logger.info("Compared classifier: %s | acc=%.4f", algo, rows[-1]["accuracy"])
        except Exception as exc:
            logger.warning("Comparison failed for %s: %s", algo, exc)
            rows.append({"algorithm": algo, "error": str(exc)})

    rows.sort(key=lambda d: d.get("f1_weighted", -1), reverse=True)
    return rows


def compare_regression_models(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    algorithms: list[str] | None = None,
    random_state: int = 42,
) -> list[dict[str, Any]]:
    """Train multiple regressors on the same split and return a ranking table.

    Returns
    -------
    list[dict]
        Rows sorted by ``rmse`` ascending (lower is better).
    """
    algos = algorithms or ["random_forest", "linear_regression", "ridge"]
    rows: list[dict[str, Any]] = []

    for algo in algos:
        try:
            model = RegressionModel(algorithm=algo, random_state=random_state)
            model.train(X_train, y_train)
            y_pred = model.predict(X_test)
            mse = float(mean_squared_error(y_test, y_pred))
            rows.append({
                "algorithm": algo,
                "rmse": round(float(np.sqrt(mse)), 4),
                "r2": round(float(r2_score(y_test, y_pred)), 4),
                "train_rows": int(len(X_train)),
                "test_rows": int(len(X_test)),
            })
            logger.info("Compared regressor: %s | rmse=%.4f", algo, rows[-1]["rmse"])
        except Exception as exc:
            logger.warning("Comparison failed for %s: %s", algo, exc)
            rows.append({"algorithm": algo, "error": str(exc)})

    rows.sort(key=lambda d: d.get("rmse", float("inf")))
    return rows
