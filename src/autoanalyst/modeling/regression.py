"""Enhanced regression model wrapper — Team 5."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor

logger = logging.getLogger(__name__)

_SUPPORTED_ALGORITHMS = frozenset(
    {"random_forest", "linear_regression", "ridge", "lasso", "decision_tree"}
)


def _validate_features(X: Any) -> None:
    if isinstance(X, pd.DataFrame):
        bad = list(X.select_dtypes(exclude=[np.number, bool, "bool", "boolean"]).columns)
        if bad:
            raise ValueError(
                f"Features contain non-numeric columns: {bad}. Encode them first."
            )
        if X.isna().any().any():
            raise ValueError("Features contain NaN values. Impute them first.")
    elif isinstance(X, np.ndarray):
        if np.isnan(X).any():
            raise ValueError("Features contain NaN values.")


class RegressionModel:
    """Unified wrapper around scikit-learn regression estimators.

    Parameters
    ----------
    algorithm:
        One of ``'random_forest'``, ``'linear_regression'``,
        ``'ridge'``, ``'lasso'``, ``'decision_tree'``.
    hyperparameters:
        Optional estimator keyword arguments.
    random_state:
        Global random seed.
    """

    def __init__(
        self,
        algorithm: str = "random_forest",
        hyperparameters: dict[str, Any] | None = None,
        random_state: int = 42,
    ) -> None:
        algo = algorithm.lower()
        if algo not in _SUPPORTED_ALGORITHMS:
            raise ValueError(
                f"Unsupported algorithm '{algorithm}'. "
                f"Choose from: {sorted(_SUPPORTED_ALGORITHMS)}."
            )
        self.algorithm = algo
        self.random_state = random_state
        self._is_trained = False

        hp = dict(hyperparameters or {})
        # Only tree-based models accept random_state
        if algo in {"random_forest", "decision_tree"}:
            hp.setdefault("random_state", random_state)

        if algo == "random_forest":
            hp.setdefault("n_estimators", 100)
            self.model: Any = RandomForestRegressor(**hp)
        elif algo == "linear_regression":
            # LinearRegression does not accept random_state
            hp.pop("random_state", None)
            self.model = LinearRegression(**hp)
        elif algo == "ridge":
            hp.pop("random_state", None)
            self.model = Ridge(**hp)
        elif algo == "lasso":
            hp.pop("random_state", None)
            self.model = Lasso(**hp)
        elif algo == "decision_tree":
            self.model = DecisionTreeRegressor(**hp)

    # ── Public methods ────────────────────────────────────────────────────────

    def train(
        self,
        X: pd.DataFrame | np.ndarray,
        y: pd.Series | np.ndarray,
        test_size: float | None = None,
    ) -> Any:
        """Fit the regressor on training data.

        If test_size is provided, splits data, fits on train split, and returns
        (X_train, X_test, y_train, y_test) for backward compatibility.
        """
        if test_size is not None:
            return self.train_and_split(X, y, test_size=test_size)

        _validate_features(X)
        if len(y) == 0:
            raise ValueError("Target y is empty.")
        self.model.fit(X, y)
        self._is_trained = True
        logger.info("RegressionModel (%s) fitted on %d samples.", self.algorithm, len(y))

    def predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Return predicted numeric values."""
        self._check_fitted()
        _validate_features(X)
        return self.model.predict(X)

    # ── Legacy helper kept for pipeline.py compatibility ──────────────────────

    def train_and_split(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Split, train, and return (X_train, X_test, y_train, y_test)."""
        _validate_features(X)
        if X.empty or y.empty:
            raise ValueError("Features and target must not be empty.")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state
        )
        self.model.fit(X_train, y_train)
        self._is_trained = True
        return X_train, X_test, y_train, y_test

    # ── Internals ─────────────────────────────────────────────────────────────

    def _check_fitted(self) -> None:
        if not self._is_trained:
            raise ValueError("Model has not been trained yet. Call train() first.")
