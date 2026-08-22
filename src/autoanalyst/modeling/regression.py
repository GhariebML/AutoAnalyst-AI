"""Starter regression model wrapper."""

from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_validate, train_test_split


class RegressionModel:
    """RandomForest regressor helper with configurable hyperparameters."""

    def __init__(self, random_state: int = 42, **hyperparameters: Any) -> None:
        self.random_state = random_state
        self.hyperparameters: dict[str, Any] = {"random_state": random_state, **hyperparameters}
        self.model = RandomForestRegressor(**self.hyperparameters)

    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
        """Split data, train the model, and return train/test sets."""
        if X.empty or y.empty:
            raise ValueError("Features and target must not be empty.")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state
        )
        self.model.fit(X_train, y_train)
        return X_train, X_test, y_train, y_test

    def predict(self, X: pd.DataFrame):
        """Generate numeric predictions."""
        return self.model.predict(X)

    def cross_validate(self, X: pd.DataFrame, y: pd.Series, cv: int = 5) -> dict[str, Any]:
        """Run k-fold cross-validation and return R²/RMSE aggregates."""
        if X.empty or y.empty:
            raise ValueError("Features and target must not be empty.")
        scores = cross_validate(self.model, X, y, cv=cv, scoring=("r2", "neg_root_mean_squared_error"))
        rmse_scores = -scores["test_neg_root_mean_squared_error"]
        return {
            "task": "regression",
            "folds": int(cv),
            "r2_mean": round(float(scores["test_r2"].mean()), 6),
            "r2_std": round(float(scores["test_r2"].std()), 6),
            "rmse_mean": round(float(rmse_scores.mean()), 6),
            "rmse_std": round(float(rmse_scores.std()), 6),
        }

    def save(self, path: str | Path) -> Path:
        """Persist the fitted estimator with joblib."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, target)
        return target

    @classmethod
    def load(cls, path: str | Path) -> "RegressionModel":
        """Load a previously saved estimator."""
        instance = cls()
        instance.model = joblib.load(path)
        return instance
