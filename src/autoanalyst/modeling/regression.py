"""Regression model wrappers, automated multi-model benchmarking, and hyperparameter tuning."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Literal

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import ElasticNet, Lasso, LinearRegression, Ridge
from sklearn.model_selection import KFold, RandomizedSearchCV, cross_validate, train_test_split

logger = logging.getLogger(__name__)


class RegressionModel:
    """Versatile regression model wrapper with support for multiple algorithms."""

    def __init__(
        self,
        model_type: Literal[
            "random_forest", "gradient_boosting", "linear", "ridge", "lasso", "elastic_net"
        ] = "random_forest",
        random_state: int = 42,
        **hyperparameters: Any,
    ) -> None:
        self.model_type = model_type
        self.random_state = random_state
        self.hyperparameters = {"random_state": random_state, **hyperparameters}

        if model_type == "random_forest":
            self.model = RandomForestRegressor(**self.hyperparameters)
        elif model_type == "gradient_boosting":
            self.model = GradientBoostingRegressor(**self.hyperparameters)
        elif model_type == "linear":
            self.model = LinearRegression()
        elif model_type == "ridge":
            self.model = Ridge(
                random_state=random_state, **{k: v for k, v in self.hyperparameters.items() if k != "random_state"}
            )
        elif model_type == "lasso":
            self.model = Lasso(
                random_state=random_state, **{k: v for k, v in self.hyperparameters.items() if k != "random_state"}
            )
        elif model_type == "elastic_net":
            self.model = ElasticNet(
                random_state=random_state, **{k: v for k, v in self.hyperparameters.items() if k != "random_state"}
            )
        else:
            raise ValueError(f"Unknown model_type '{model_type}'.")

    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
        """Split data, fit the model on the training fold, and return splits."""
        if X.empty or y.empty:
            raise ValueError("Features and target must not be empty.")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=self.random_state)
        self.model.fit(X_train, y_train)
        return X_train, X_test, y_train, y_test

    def predict(self, X: pd.DataFrame):
        """Generate continuous target predictions."""
        return self.model.predict(X)

    def cross_validate(self, X: pd.DataFrame, y: pd.Series, cv: int = 5) -> dict[str, Any]:
        """Run k-fold cross-validation and return RMSE/MAE/R2 aggregates."""
        if X.empty or y.empty:
            raise ValueError("Features and target must not be empty.")
        kf = KFold(n_splits=cv, shuffle=True, random_state=self.random_state)
        scores = cross_validate(
            self.model,
            X,
            y,
            cv=kf,
            scoring=("neg_root_mean_squared_error", "neg_mean_absolute_error", "r2"),
        )
        return {
            "task": "regression",
            "model_name": type(self.model).__name__,
            "folds": int(cv),
            "rmse_mean": round(float(-scores["test_neg_root_mean_squared_error"].mean()), 6),
            "rmse_std": round(float(scores["test_neg_root_mean_squared_error"].std()), 6),
            "mae_mean": round(float(-scores["test_neg_mean_absolute_error"].mean()), 6),
            "mae_std": round(float(scores["test_neg_mean_absolute_error"].std()), 6),
            "r2_mean": round(float(scores["test_r2"].mean()), 6),
            "r2_std": round(float(scores["test_r2"].std()), 6),
        }

    def tune_hyperparameters(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        param_distributions: dict[str, Any] | None = None,
        n_iter: int = 10,
        cv: int = 3,
    ) -> dict[str, Any]:
        """Perform randomized hyperparameter search and update the fitted estimator."""
        if param_distributions is None:
            if isinstance(self.model, RandomForestRegressor):
                param_distributions = {
                    "n_estimators": [50, 100, 200],
                    "max_depth": [None, 5, 10, 20],
                    "min_samples_split": [2, 5, 10],
                }
            elif isinstance(self.model, GradientBoostingRegressor):
                param_distributions = {
                    "n_estimators": [50, 100, 150],
                    "learning_rate": [0.01, 0.05, 0.1],
                    "max_depth": [3, 5, 7],
                }
            else:
                param_distributions = {"alpha": [0.01, 0.1, 1.0, 10.0]}

        search = RandomizedSearchCV(
            self.model,
            param_distributions=param_distributions,
            n_iter=n_iter,
            cv=cv,
            scoring="neg_root_mean_squared_error",
            random_state=self.random_state,
        )
        search.fit(X, y)
        self.model = search.best_estimator_
        return {
            "best_params": search.best_params_,
            "best_rmse": round(float(-search.best_score_), 6),
        }

    def get_feature_importances(self, feature_names: list[str]) -> dict[str, float]:
        """Extract sorted feature importances from fitted estimator."""
        if hasattr(self.model, "feature_importances_"):
            importances = self.model.feature_importances_
            return {
                name: round(float(imp), 6)
                for name, imp in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
            }
        elif hasattr(self.model, "coef_"):
            coef = np.abs(self.model.coef_)
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
    def load(cls, path: str | Path) -> RegressionModel:
        """Load a previously saved estimator."""
        instance = cls()
        instance.model = joblib.load(path)
        return instance


def benchmark_regression_models(
    X: pd.DataFrame,
    y: pd.Series,
    random_state: int = 42,
    cv: int = 5,
    metric: Literal["rmse", "mae", "r2"] = "rmse",
) -> tuple[pd.DataFrame, RegressionModel]:
    """Benchmark a zoo of regression models and return a leaderboard and the champion regressor."""
    candidates = [
        ("RandomForestRegressor", RandomForestRegressor(random_state=random_state, n_estimators=100)),
        ("GradientBoostingRegressor", GradientBoostingRegressor(random_state=random_state)),
        ("Ridge", Ridge(random_state=random_state)),
        ("Lasso", Lasso(random_state=random_state)),
        ("LinearRegression", LinearRegression()),
    ]

    leaderboard_rows: list[dict[str, Any]] = []
    fitted_models: dict[str, Any] = {}
    kf = KFold(n_splits=cv, shuffle=True, random_state=random_state)

    for name, estimator in candidates:
        try:
            scores = cross_validate(
                estimator,
                X,
                y,
                cv=kf,
                scoring=("neg_root_mean_squared_error", "neg_mean_absolute_error", "r2"),
            )
            rmse_mean = float(-scores["test_neg_root_mean_squared_error"].mean())
            rmse_std = float(scores["test_neg_root_mean_squared_error"].std())
            mae_mean = float(-scores["test_neg_mean_absolute_error"].mean())
            mae_std = float(scores["test_neg_mean_absolute_error"].std())
            r2_mean = float(scores["test_r2"].mean())
            r2_std = float(scores["test_r2"].std())

            leaderboard_rows.append(
                {
                    "model_name": name,
                    "rmse_mean": round(rmse_mean, 4),
                    "rmse_std": round(rmse_std, 4),
                    "mae_mean": round(mae_mean, 4),
                    "mae_std": round(mae_std, 4),
                    "r2_mean": round(r2_mean, 4),
                    "r2_std": round(r2_std, 4),
                }
            )
            fitted_models[name] = estimator
        except Exception as exc:
            logger.warning("Benchmarking regressor '%s' failed: %s", name, exc)

    if not leaderboard_rows:
        rf = RegressionModel(model_type="random_forest", random_state=random_state)
        return pd.DataFrame([{"model_name": "RandomForestRegressor", "rmse_mean": 0.0, "r2_mean": 0.0}]), rf

    ascending = metric in {"rmse", "mae"}
    sort_col = f"{metric}_mean"
    leaderboard = pd.DataFrame(leaderboard_rows).sort_values(sort_col, ascending=ascending).reset_index(drop=True)

    champion_name = str(leaderboard.iloc[0]["model_name"])
    champion_wrapper = RegressionModel(random_state=random_state)
    champion_wrapper.model = fitted_models[champion_name]

    return leaderboard, champion_wrapper
