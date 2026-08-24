"""Unit tests for the modeling engine (classification & regression benchmarking)."""

from __future__ import annotations

import pandas as pd
import pytest

from autoanalyst.modeling.classification import ClassificationModel, benchmark_classification_models
from autoanalyst.modeling.regression import RegressionModel, benchmark_regression_models


@pytest.fixture
def classification_data() -> tuple[pd.DataFrame, pd.Series]:
    df = pd.DataFrame(
        {
            "feat1": [1.0, 2.0, 1.5, 8.0, 9.0, 8.5] * 10,
            "feat2": [2.0, 1.0, 1.8, 9.0, 8.0, 8.8] * 10,
            "target": [0, 0, 0, 1, 1, 1] * 10,
        }
    )
    return df[["feat1", "feat2"]], df["target"]


@pytest.fixture
def regression_data() -> tuple[pd.DataFrame, pd.Series]:
    df = pd.DataFrame(
        {
            "feat1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0] * 10,
            "feat2": [0.5, 1.0, 1.5, 2.0, 2.5, 3.0] * 10,
            "target": [2.5, 5.0, 7.5, 10.0, 12.5, 15.0] * 10,
        }
    )
    return df[["feat1", "feat2"]], df["target"]


class TestClassificationEngine:
    def test_single_classifier_train_predict(self, classification_data: tuple[pd.DataFrame, pd.Series]) -> None:
        X, y = classification_data
        clf = ClassificationModel(model_type="random_forest", random_state=42)
        X_train, X_test, y_train, y_test = clf.train(X, y, test_size=0.3)
        preds = clf.predict(X_test)
        assert len(preds) == len(X_test)

        cv_results = clf.cross_validate(X, y, cv=3)
        assert cv_results["accuracy_mean"] > 0.8
        assert "f1_macro_mean" in cv_results

    def test_benchmark_classification_models(self, classification_data: tuple[pd.DataFrame, pd.Series]) -> None:
        X, y = classification_data
        leaderboard, champion = benchmark_classification_models(X, y, cv=3)
        assert isinstance(leaderboard, pd.DataFrame)
        assert len(leaderboard) >= 3
        assert "model_name" in leaderboard.columns
        assert "f1_macro_mean" in leaderboard.columns
        assert isinstance(champion, ClassificationModel)


class TestRegressionEngine:
    def test_single_regressor_train_predict(self, regression_data: tuple[pd.DataFrame, pd.Series]) -> None:
        X, y = regression_data
        reg = RegressionModel(model_type="linear", random_state=42)
        X_train, X_test, y_train, y_test = reg.train(X, y, test_size=0.3)
        preds = reg.predict(X_test)
        assert len(preds) == len(X_test)

        cv_results = reg.cross_validate(X, y, cv=3)
        assert cv_results["r2_mean"] > 0.9

    def test_benchmark_regression_models(self, regression_data: tuple[pd.DataFrame, pd.Series]) -> None:
        X, y = regression_data
        leaderboard, champion = benchmark_regression_models(X, y, cv=3)
        assert isinstance(leaderboard, pd.DataFrame)
        assert len(leaderboard) >= 3
        assert "rmse_mean" in leaderboard.columns
        assert isinstance(champion, RegressionModel)
