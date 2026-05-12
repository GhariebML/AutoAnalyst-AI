"""Model evaluation functions for classification and regression."""

from typing import Any

from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error, mean_squared_error, r2_score


def evaluate_classification(y_true, y_pred) -> dict[str, Any]:
    """Return basic classification metrics."""
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "classification_report": classification_report(y_true, y_pred, output_dict=True, zero_division=0),
    }


def evaluate_regression(y_true, y_pred) -> dict[str, float]:
    """Return basic regression metrics."""
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "mse": float(mean_squared_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }
