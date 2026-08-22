"""Starter classification model wrapper."""

from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_validate, train_test_split


class ClassificationModel:
    """RandomForest classifier helper with configurable hyperparameters."""

    def __init__(self, random_state: int = 42, **hyperparameters: Any) -> None:
        self.random_state = random_state
        self.hyperparameters: dict[str, Any] = {"random_state": random_state, **hyperparameters}
        self.model = RandomForestClassifier(**self.hyperparameters)

    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
        """Split data, train the model, and return train/test sets."""
        if X.empty or y.empty:
            raise ValueError("Features and target must not be empty.")
        stratify = y if y.nunique() > 1 and y.value_counts().min() > 1 else None
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state, stratify=stratify
        )
        self.model.fit(X_train, y_train)
        return X_train, X_test, y_train, y_test

    def predict(self, X: pd.DataFrame):
        """Generate class predictions."""
        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame):
        """Generate class probability estimates."""
        return self.model.predict_proba(X)

    def cross_validate(self, X: pd.DataFrame, y: pd.Series, cv: int = 5) -> dict[str, Any]:
        """Run k-fold cross-validation and return accuracy/F1 aggregates."""
        if X.empty or y.empty:
            raise ValueError("Features and target must not be empty.")
        scores = cross_validate(self.model, X, y, cv=cv, scoring=("accuracy", "f1_macro"))
        return {
            "task": "classification",
            "folds": int(cv),
            "accuracy_mean": round(float(scores["test_accuracy"].mean()), 6),
            "accuracy_std": round(float(scores["test_accuracy"].std()), 6),
            "f1_macro_mean": round(float(scores["test_f1_macro"].mean()), 6),
            "f1_macro_std": round(float(scores["test_f1_macro"].std()), 6),
        }

    def save(self, path: str | Path) -> Path:
        """Persist the fitted estimator with joblib."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, target)
        return target

    @classmethod
    def load(cls, path: str | Path) -> "ClassificationModel":
        """Load a previously saved estimator."""
        instance = cls()
        instance.model = joblib.load(path)
        return instance
