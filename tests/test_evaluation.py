"""Unit tests for the evaluation and model diagnostics module."""

from __future__ import annotations

import numpy as np
import pytest

from autoanalyst.evaluation.evaluator import evaluate_classification, evaluate_regression


class TestEvaluationEngine:
    def test_evaluate_classification(self) -> None:
        y_true = np.array([0, 1, 0, 1, 0, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 1, 0, 0, 0, 1])
        y_proba = np.array(
            [
                [0.9, 0.1],
                [0.2, 0.8],
                [0.8, 0.2],
                [0.3, 0.7],
                [0.7, 0.3],
                [0.6, 0.4],
                [0.85, 0.15],
                [0.1, 0.9],
            ]
        )

        metrics = evaluate_classification(y_true, y_pred, y_proba=y_proba)
        assert "accuracy" in metrics
        assert "f1_macro" in metrics
        assert "confusion_matrix" in metrics
        assert "roc_auc" in metrics
        assert "brier_score" in metrics
        assert "threshold_optimization" in metrics
        assert metrics["accuracy"] == 0.875

    def test_evaluate_regression(self) -> None:
        y_true = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        y_pred = np.array([11.0, 19.0, 31.0, 39.0, 52.0])

        metrics = evaluate_regression(y_true, y_pred, n_features=2)
        assert "mae" in metrics
        assert "rmse" in metrics
        assert "r2" in metrics
        assert "adjusted_r2" in metrics
        assert "residuals_summary" in metrics
        assert metrics["mae"] == pytest.approx(1.2)
