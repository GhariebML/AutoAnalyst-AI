"""Model evaluation functions for classification and regression."""

from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)


def evaluate_classification(
    y_true: Any,
    y_pred: Any,
    y_proba: Any = None,
    labels: Any = None,
) -> dict[str, Any]:
    """Return flattened classification metrics plus detailed report artifacts.

    When ``y_proba`` (array of shape ``(n_samples, n_classes)``) is supplied,
    a macro-average ROC-AUC is added when computable; otherwise it is omitted
    silently so evaluation never blocks the pipeline. ``labels`` pins the
    confusion-matrix/report label set so degenerate splits stay well-shaped.
    """
    result: dict[str, Any] = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_weighted": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "classification_report": classification_report(
            y_true, y_pred, output_dict=True, zero_division=0, labels=labels
        ),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
    }

    roc_auc = _safe_roc_auc(y_true, y_proba)
    if roc_auc is not None:
        result["roc_auc"] = roc_auc
    return result


def evaluate_regression(y_true: Any, y_pred: Any) -> dict[str, float]:
    """Return regression metrics including RMSE."""
    mse = float(mean_squared_error(y_true, y_pred))
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "mse": mse,
        "rmse": float(np.sqrt(mse)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def _safe_roc_auc(y_true: Any, y_proba: Any) -> float | None:
    """Compute ROC-AUC defensively; return None when not computable."""
    if y_proba is None:
        return None
    proba = np.asarray(y_proba)
    labels = np.unique(np.asarray(y_true))
    if labels.size < 2 or proba.ndim < 2 or proba.shape[-1] < 2:
        return None
    try:
        if proba.shape[-1] == 2:
            return float(roc_auc_score(y_true, proba[:, 1]))
        return float(roc_auc_score(y_true, proba, multi_class="ovr", average="macro"))
    except (ValueError, IndexError):
        return None
