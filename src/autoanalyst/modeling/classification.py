"""Classification model wrappers, automated multi-model benchmarking, and hyperparameter tuning."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, cross_validate, train_test_split
from sklearn.tree import DecisionTreeClassifier

logger = logging.getLogger(__name__)


@dataclass
class ModelCandidate:
    """Evaluation result for a single candidate model during benchmarking."""

    name: str
    accuracy_mean: float
    accuracy_std: float
    f1_macro_mean: float
    f1_macro_std: float
    roc_auc_mean: float | None
    estimator: Any


class ClassificationModel:
    """Versatile classification model wrapper with support for multiple algorithms."""

    def __init__(
        self,
        model_type: Literal[
            "random_forest", "gradient_boosting", "logistic_regression", "extra_trees", "decision_tree"
        ] = "random_forest",
        random_state: int = 42,
        **hyperparameters: Any,
    ) -> None:
        self.model_type = model_type
        self.random_state = random_state
        self.hyperparameters = {"random_state": random_state, **hyperparameters}

        if model_type == "random_forest":
            self.model = RandomForestClassifier(**self.hyperparameters)
        elif model_type == "gradient_boosting":
            self.model = GradientBoostingClassifier(**self.hyperparameters)
        elif model_type == "logistic_regression":
            # Remove random_state if solver doesn't use it, but standard solvers do
            params = {k: v for k, v in self.hyperparameters.items() if k != "random_state"}
            self.model = LogisticRegression(random_state=random_state, max_iter=1000, **params)
        elif model_type == "extra_trees":
            self.model = ExtraTreesClassifier(**self.hyperparameters)
        elif model_type == "decision_tree":
            self.model = DecisionTreeClassifier(**self.hyperparameters)
        else:
            raise ValueError(f"Unknown model_type '{model_type}'.")

    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
        """Split data, fit the model on the training fold, and return splits."""
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
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X)
        return None

    def cross_validate(self, X: pd.DataFrame, y: pd.Series, cv: int = 5) -> dict[str, Any]:
        """Run k-fold cross-validation and return accuracy/F1 aggregates."""
        if X.empty or y.empty:
            raise ValueError("Features and target must not be empty.")
        cv_splitter = (
            StratifiedKFold(n_splits=cv, shuffle=True, random_state=self.random_state) if y.nunique() > 1 else cv
        )
        scores = cross_validate(self.model, X, y, cv=cv_splitter, scoring=("accuracy", "f1_macro"))
        return {
            "task": "classification",
            "model_name": type(self.model).__name__,
            "folds": int(cv),
            "accuracy_mean": round(float(scores["test_accuracy"].mean()), 6),
            "accuracy_std": round(float(scores["test_accuracy"].std()), 6),
            "f1_macro_mean": round(float(scores["test_f1_macro"].mean()), 6),
            "f1_macro_std": round(float(scores["test_f1_macro"].std()), 6),
        }

    def tune_hyperparameters(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        param_distributions: dict[str, Any] | None = None,
        n_iter: int = 10,
        cv: int = 3,
    ) -> dict[str, Any]:
        """Perform randomized hyperparameter optimization and update estimator."""
        if param_distributions is None:
            if isinstance(self.model, (RandomForestClassifier, ExtraTreesClassifier)):
                param_distributions = {
                    "n_estimators": [50, 100, 200],
                    "max_depth": [None, 5, 10, 20],
                    "min_samples_split": [2, 5, 10],
                }
            elif isinstance(self.model, GradientBoostingClassifier):
                param_distributions = {
                    "n_estimators": [50, 100, 150],
                    "learning_rate": [0.01, 0.05, 0.1, 0.2],
                    "max_depth": [3, 5, 7],
                }
            else:
                param_distributions = {"C": [0.01, 0.1, 1.0, 10.0]}

        search = RandomizedSearchCV(
            self.model,
            param_distributions=param_distributions,
            n_iter=n_iter,
            cv=cv,
            scoring="f1_macro",
            random_state=self.random_state,
        )
        search.fit(X, y)
        self.model = search.best_estimator_
        return {
            "best_params": search.best_params_,
            "best_score": round(float(search.best_score_), 6),
        }

    def get_feature_importances(self, feature_names: list[str]) -> dict[str, float]:
        """Extract sorted feature importances from fitted model."""
        if hasattr(self.model, "feature_importances_"):
            importances = self.model.feature_importances_
            return {
                name: round(float(imp), 6)
                for name, imp in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
            }
        elif hasattr(self.model, "coef_"):
            coef = np.abs(self.model.coef_).mean(axis=0)
            return {
                name: round(float(c), 6)
                for name, c in sorted(zip(feature_names, coef), key=lambda x: x[1], reverse=True)
            }
        return {}

    def save(self, path: str | Path) -> Path:
        """Persist the fitted estimator with joblib."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, target)
        return target

    @classmethod
    def load(cls, path: str | Path) -> ClassificationModel:
        """Load a previously saved estimator."""
        instance = cls()
        instance.model = joblib.load(path)
        return instance


def benchmark_classification_models(
    X: pd.DataFrame,
    y: pd.Series,
    random_state: int = 42,
    cv: int = 5,
    metric: Literal["f1_macro", "accuracy", "roc_auc"] = "f1_macro",
) -> tuple[pd.DataFrame, ClassificationModel]:
    """Benchmark a zoo of classification models and return a leaderboard and the champion model."""
    candidates = [
        ("RandomForestClassifier", RandomForestClassifier(random_state=random_state, n_estimators=100)),
        ("GradientBoostingClassifier", GradientBoostingClassifier(random_state=random_state)),
        ("LogisticRegression", LogisticRegression(random_state=random_state, max_iter=1000)),
        ("ExtraTreesClassifier", ExtraTreesClassifier(random_state=random_state, n_estimators=100)),
        ("DecisionTreeClassifier", DecisionTreeClassifier(random_state=random_state)),
    ]

    leaderboard_rows: list[dict[str, Any]] = []
    fitted_models: dict[str, Any] = {}

    cv_splitter = StratifiedKFold(n_splits=cv, shuffle=True, random_state=random_state) if y.nunique() > 1 else cv

    for name, estimator in candidates:
        try:
            scores = cross_validate(estimator, X, y, cv=cv_splitter, scoring=("accuracy", "f1_macro"))
            acc_mean = float(scores["test_accuracy"].mean())
            acc_std = float(scores["test_accuracy"].std())
            f1_mean = float(scores["test_f1_macro"].mean())
            f1_std = float(scores["test_f1_macro"].std())

            leaderboard_rows.append(
                {
                    "model_name": name,
                    "f1_macro_mean": round(f1_mean, 4),
                    "f1_macro_std": round(f1_std, 4),
                    "accuracy_mean": round(acc_mean, 4),
                    "accuracy_std": round(acc_std, 4),
                }
            )
            fitted_models[name] = estimator
        except Exception as exc:
            logger.warning("Benchmarking model '%s' failed: %s", name, exc)

    if not leaderboard_rows:
        # Fallback to standard Random Forest
        rf = ClassificationModel(model_type="random_forest", random_state=random_state)
        return pd.DataFrame([{"model_name": "RandomForestClassifier", "f1_macro_mean": 0.0, "accuracy_mean": 0.0}]), rf

    sort_col = "f1_macro_mean" if metric == "f1_macro" else "accuracy_mean"
    leaderboard = pd.DataFrame(leaderboard_rows).sort_values(sort_col, ascending=False).reset_index(drop=True)

    champion_name = str(leaderboard.iloc[0]["model_name"])
    champion_wrapper = ClassificationModel(random_state=random_state)
    champion_wrapper.model = fitted_models[champion_name]

    return leaderboard, champion_wrapper
