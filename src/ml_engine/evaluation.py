"""Evaluation metrics for classification, regression, and clustering models."""

import logging
from typing import Any
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    davies_bouldin_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    silhouette_score,
)

logger = logging.getLogger(__name__)


def _make_serializable(val: Any) -> Any:
    """Recursively convert NumPy types to native Python types for JSON serialization."""
    if isinstance(val, dict):
        return {k: _make_serializable(v) for k, v in val.items()}
    elif isinstance(val, (list, tuple)):
        return [_make_serializable(v) for v in val]
    elif isinstance(val, np.ndarray):
        return val.tolist()
    elif isinstance(val, (np.integer, np.signedinteger)):
        return int(val)
    elif isinstance(val, np.floating):
        return float(val)
    elif isinstance(val, np.bool_):
        return bool(val)
    return val


def evaluate_classification(
    y_true: Any,
    y_pred: Any,
    y_prob: Any = None,
) -> dict[str, Any]:
    """Calculate standard classification evaluation metrics.

    Parameters
    ----------
    y_true : array-like
        True labels.
    y_pred : array-like
        Predicted labels.
    y_prob : array-like, optional
        Predicted class probabilities. Can be 1D (probabilities of the positive class)
        or 2D (probabilities for each class).

    Returns
    -------
    dict
        A dictionary containing classification metrics, guaranteed to be JSON-serializable.
    """
    if y_true is None or y_pred is None:
        raise ValueError("y_true and y_pred cannot be None.")
    
    y_true_arr = np.asarray(y_true)
    y_pred_arr = np.asarray(y_pred)

    if len(y_true_arr) == 0 or len(y_pred_arr) == 0:
        raise ValueError("y_true and y_pred cannot be empty.")
    if len(y_true_arr) != len(y_pred_arr):
        raise ValueError("y_true and y_pred must have the same length.")

    metrics: dict[str, Any] = {
        "accuracy": float(accuracy_score(y_true_arr, y_pred_arr)),
        "precision_macro": float(precision_score(y_true_arr, y_pred_arr, average="macro", zero_division=0)),
        "precision_weighted": float(precision_score(y_true_arr, y_pred_arr, average="weighted", zero_division=0)),
        "recall_macro": float(recall_score(y_true_arr, y_pred_arr, average="macro", zero_division=0)),
        "recall_weighted": float(recall_score(y_true_arr, y_pred_arr, average="weighted", zero_division=0)),
        "f1_macro": float(f1_score(y_true_arr, y_pred_arr, average="macro", zero_division=0)),
        "f1_weighted": float(f1_score(y_true_arr, y_pred_arr, average="weighted", zero_division=0)),
        "confusion_matrix": confusion_matrix(y_true_arr, y_pred_arr).tolist(),
        "classification_report": classification_report(y_true_arr, y_pred_arr, output_dict=True, zero_division=0),
    }

    if y_prob is not None:
        try:
            y_prob_arr = np.asarray(y_prob)
            unique_classes = np.unique(y_true_arr)
            
            if len(unique_classes) == 2:
                # If 2D prob array is passed, use the probabilities of the positive class
                if y_prob_arr.ndim == 2 and y_prob_arr.shape[1] == 2:
                    metrics["roc_auc"] = float(roc_auc_score(y_true_arr, y_prob_arr[:, 1]))
                else:
                    metrics["roc_auc"] = float(roc_auc_score(y_true_arr, y_prob_arr))
            else:
                # Multiclass ROC AUC (One-vs-Rest)
                metrics["roc_auc"] = float(roc_auc_score(y_true_arr, y_prob_arr, multi_class="ovr"))
        except Exception as exc:
            logger.warning(f"Could not compute ROC-AUC: {exc}")
            metrics["roc_auc"] = None

    return _make_serializable(metrics)


def evaluate_regression(y_true: Any, y_pred: Any) -> dict[str, Any]:
    """Calculate standard regression evaluation metrics.

    Parameters
    ----------
    y_true : array-like
        True target values.
    y_pred : array-like
        Predicted target values.

    Returns
    -------
    dict
        A dictionary containing regression metrics (mse, rmse, mae, r2),
        guaranteed to be JSON-serializable.
    """
    if y_true is None or y_pred is None:
        raise ValueError("y_true and y_pred cannot be None.")
    
    y_true_arr = np.asarray(y_true)
    y_pred_arr = np.asarray(y_pred)

    if len(y_true_arr) == 0 or len(y_pred_arr) == 0:
        raise ValueError("y_true and y_pred cannot be empty.")
    if len(y_true_arr) != len(y_pred_arr):
        raise ValueError("y_true and y_pred must have the same length.")

    mse = mean_squared_error(y_true_arr, y_pred_arr)
    metrics = {
        "mse": float(mse),
        "rmse": float(np.sqrt(mse)),
        "mae": float(mean_absolute_error(y_true_arr, y_pred_arr)),
        "r2": float(r2_score(y_true_arr, y_pred_arr)),
    }

    return _make_serializable(metrics)


def evaluate_clustering(X: Any, labels: Any) -> dict[str, Any]:
    """Calculate clustering evaluation metrics.

    Parameters
    ----------
    X : array-like or pd.DataFrame
        Input features.
    labels : array-like
        Cluster labels assigned to each sample.

    Returns
    -------
    dict
        A dictionary containing clustering metrics (silhouette_score, davies_bouldin_index),
        guaranteed to be JSON-serializable. Returns None for metrics if evaluation is not possible.
    """
    if X is None or labels is None:
        raise ValueError("X and labels cannot be None.")
    
    # Support DataFrame/Series
    X_arr = np.asarray(X)
    labels_arr = np.asarray(labels)

    if len(X_arr) == 0 or len(labels_arr) == 0:
        raise ValueError("X and labels cannot be empty.")
    if len(X_arr) != len(labels_arr):
        raise ValueError("X and labels must have the same length.")

    unique_labels = np.unique(labels_arr)
    
    # Filter out noise label (-1) to see if we have actual clusters for silhouette/DB index
    non_noise_mask = labels_arr != -1
    unique_non_noise = np.unique(labels_arr[non_noise_mask])

    metrics: dict[str, Any] = {
        "silhouette_score": None,
        "davies_bouldin_index": None,
        "n_clusters": int(len(unique_non_noise)),
        "noise_count": int(np.sum(~non_noise_mask)),
    }

    # Silhouette and Davies-Bouldin require at least 2 distinct clusters
    # in the data passed to the scorer (and sample size > number of clusters).
    # If we include the noise cluster -1, unique_labels has size. Let's see if we have
    # at least 2 unique labels overall (since sklearn allows passing -1 as a valid class).
    if len(unique_labels) >= 2 and len(unique_labels) < len(X_arr):
        try:
            metrics["silhouette_score"] = float(silhouette_score(X_arr, labels_arr))
            metrics["davies_bouldin_index"] = float(davies_bouldin_score(X_arr, labels_arr))
        except Exception as exc:
            logger.warning(f"Error computing clustering metrics: {exc}")

    return _make_serializable(metrics)
