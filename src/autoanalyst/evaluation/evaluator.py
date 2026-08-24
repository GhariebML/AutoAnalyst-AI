"""Model evaluation and comprehensive performance diagnostics for classification and regression."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    explained_variance_score,
    f1_score,
    matthews_corrcoef,
    max_error,
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)

logger = logging.getLogger(__name__)


def evaluate_classification(
    y_true: Any,
    y_pred: Any,
    y_proba: Any = None,
    labels: Any = None,
) -> dict[str, Any]:
    """Calculate comprehensive classification metrics, confusion matrices, and calibration checks.

    Parameters
    ----------
    y_true:
        Ground truth class labels.
    y_pred:
        Predicted class labels.
    y_proba:
        Optional array of predicted class probabilities of shape (n_samples, n_classes).
    labels:
        Optional fixed list of class labels to preserve confusion matrix shape.
    """
    y_t = np.asarray(y_true)
    y_p = np.asarray(y_pred)

    result: dict[str, Any] = {
        "accuracy": float(accuracy_score(y_t, y_p)),
        "balanced_accuracy": float(balanced_accuracy_score(y_t, y_p)),
        "precision_macro": float(precision_score(y_t, y_p, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_t, y_p, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_t, y_p, average="macro", zero_division=0)),
        "f1_weighted": float(f1_score(y_t, y_p, average="weighted", zero_division=0)),
        "mcc": float(matthews_corrcoef(y_t, y_p)),
        "classification_report": classification_report(y_t, y_p, output_dict=True, zero_division=0, labels=labels),
        "confusion_matrix": confusion_matrix(y_t, y_p, labels=labels).tolist(),
    }

    # Normalized confusion matrix (percentages)
    cm = confusion_matrix(y_t, y_p, labels=labels)
    cm_sum = cm.sum(axis=1, keepdims=True)
    cm_norm = np.divide(cm.astype("float"), cm_sum, out=np.zeros_like(cm, dtype=float), where=cm_sum != 0)
    result["confusion_matrix_normalized"] = cm_norm.round(4).tolist()

    # ROC-AUC & Brier score
    roc_auc = _safe_roc_auc(y_t, y_proba)
    if roc_auc is not None:
        result["roc_auc"] = roc_auc

    if y_proba is not None:
        brier = _safe_brier_score(y_t, y_proba)
        if brier is not None:
            result["brier_score"] = brier

        # Threshold optimization for binary classification
        thresh_opt = _optimize_binary_threshold(y_t, y_proba)
        if thresh_opt is not None:
            result["threshold_optimization"] = thresh_opt

    return result


def evaluate_regression(
    y_true: Any,
    y_pred: Any,
    n_features: int | None = None,
) -> dict[str, Any]:
    """Calculate comprehensive regression metrics, error distributions, and residual diagnostics."""
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)

    n_samples = len(y_t)
    mse = float(mean_squared_error(y_t, y_p))
    rmse = float(np.sqrt(mse))
    mae = float(mean_absolute_error(y_t, y_p))
    r2 = float(r2_score(y_t, y_p))
    exp_var = float(explained_variance_score(y_t, y_p))
    mx_err = float(max_error(y_t, y_p))

    # Adjusted R2
    p = n_features if n_features is not None else 1
    if n_samples > p + 1:
        adj_r2 = 1.0 - (1.0 - r2) * (n_samples - 1) / (n_samples - p - 1)
    else:
        adj_r2 = r2

    # MAPE
    try:
        mape = float(mean_absolute_percentage_error(y_t, y_p))
    except Exception:
        mape = None

    # Residuals Analysis
    residuals = y_t - y_p
    res_mean = float(np.mean(residuals))
    res_std = float(np.std(residuals))
    res_skew = float(stats.skew(residuals)) if len(residuals) > 2 else 0.0

    # Homoscedasticity check (correlation between |residuals| and predicted values)
    abs_res = np.abs(residuals)
    if np.std(abs_res) > 0 and np.std(y_p) > 0:
        homoscedasticity_corr, _ = stats.pearsonr(abs_res, y_p)
    else:
        homoscedasticity_corr = 0.0

    result: dict[str, Any] = {
        "mae": round(mae, 6),
        "mse": round(mse, 6),
        "rmse": round(rmse, 6),
        "r2": round(r2, 6),
        "adjusted_r2": round(float(adj_r2), 6),
        "explained_variance": round(exp_var, 6),
        "max_error": round(mx_err, 6),
        "residuals_summary": {
            "mean": round(res_mean, 6),
            "std": round(res_std, 6),
            "skewness": round(res_skew, 4),
            "homoscedasticity_correlation": round(float(homoscedasticity_corr), 4),
        },
    }

    if mape is not None:
        result["mape"] = round(mape, 6)

    return result


def calculate_permutation_importance(
    estimator: Any,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    n_repeats: int = 5,
    random_state: int = 42,
) -> dict[str, float]:
    """Compute model-agnostic permutation feature importances on validation data."""
    try:
        perm = permutation_importance(
            estimator,
            X_val,
            y_val,
            n_repeats=n_repeats,
            random_state=random_state,
            n_jobs=-1,
        )
        importances = perm.importances_mean
        feature_names = list(X_val.columns)
        return {
            name: round(float(imp), 6)
            for name, imp in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
        }
    except Exception as exc:
        logger.warning("Permutation importance calculation failed: %s", exc)
        return {}


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
            return round(float(roc_auc_score(y_true, proba[:, 1])), 6)
        return round(float(roc_auc_score(y_true, proba, multi_class="ovr", average="macro")), 6)
    except (ValueError, IndexError):
        return None


def _safe_brier_score(y_true: Any, y_proba: Any) -> float | None:
    """Compute Brier score loss for binary classification probabilities."""
    proba = np.asarray(y_proba)
    labels = np.unique(np.asarray(y_true))
    if labels.size == 2 and proba.ndim == 2 and proba.shape[-1] == 2:
        try:
            # Assume binary target can be mapped to 0/1
            y_bin = (np.asarray(y_true) == labels[1]).astype(int)
            return round(float(brier_score_loss(y_bin, proba[:, 1])), 6)
        except Exception:
            return None
    return None


def _optimize_binary_threshold(y_true: Any, y_proba: Any) -> dict[str, Any] | None:
    """Find optimal decision threshold maximizing F1 score for binary classification."""
    proba = np.asarray(y_proba)
    labels = np.unique(np.asarray(y_true))
    if labels.size != 2 or proba.ndim != 2 or proba.shape[-1] != 2:
        return None

    try:
        y_bin = (np.asarray(y_true) == labels[1]).astype(int)
        pos_probs = proba[:, 1]

        best_thresh = 0.5
        best_f1 = 0.0

        for thresh in np.linspace(0.1, 0.9, 17):
            preds = (pos_probs >= thresh).astype(int)
            score = float(f1_score(y_bin, preds, zero_division=0))
            if score > best_f1:
                best_f1 = score
                best_thresh = float(thresh)

        return {
            "optimal_threshold": round(best_thresh, 2),
            "optimized_f1": round(best_f1, 4),
            "default_f1": round(float(f1_score(y_bin, (pos_probs >= 0.5).astype(int), zero_division=0)), 4),
        }
    except Exception:
        return None
