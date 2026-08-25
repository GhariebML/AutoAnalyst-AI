"""Enhanced classification model wrapper — Team 5."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

logger = logging.getLogger(__name__)

_SUPPORTED_ALGORITHMS = frozenset(
    {"random_forest", "logistic_regression", "svm", "decision_tree"}
)


def _validate_features(X: Any) -> None:
    """Raise informative errors for non-numeric or NaN-containing inputs."""
    if isinstance(X, pd.DataFrame):
        bad = list(X.select_dtypes(exclude=[np.number, bool, "bool", "boolean"]).columns)
        if bad:
            raise ValueError(
                f"Features contain non-numeric columns: {bad}. "
                "Please encode them before calling train()."
            )
        if X.isna().any().any():
            raise ValueError("Features contain NaN values. Impute or drop them first.")
    elif isinstance(X, np.ndarray):
        if np.isnan(X).any():
            raise ValueError("Features contain NaN values.")


class ClassificationModel:
    """Unified wrapper around scikit-learn classification estimators.

    Parameters
    ----------
    algorithm:
        One of ``'random_forest'``, ``'logistic_regression'``,
        ``'svm'``, ``'decision_tree'``.
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
        hp.setdefault("random_state", random_state)

        if algo == "random_forest":
            hp.setdefault("n_estimators", 100)
            self.model: Any = RandomForestClassifier(**hp)
        elif algo == "logistic_regression":
            hp.setdefault("max_iter", 1000)
            hp.setdefault("solver", "lbfgs")
            self.model = LogisticRegression(**hp)
        elif algo == "svm":
            # probability=True removed in sklearn 1.9; use CalibratedClassifierCV
            from sklearn.calibration import CalibratedClassifierCV
            base = SVC(random_state=random_state, **{k: v for k, v in hp.items() if k not in {"probability", "random_state"}})
            self.model = CalibratedClassifierCV(base, ensemble=False)
        elif algo == "decision_tree":
            self.model = DecisionTreeClassifier(**hp)

    # ── Public methods ────────────────────────────────────────────────────────

    def train(
        self,
        X: pd.DataFrame | np.ndarray,
        y: pd.Series | np.ndarray,
        test_size: float | None = None,
    ) -> Any:
        """Fit the classifier on training data.

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
        logger.info("ClassificationModel (%s) fitted on %d samples.", self.algorithm, len(y))

    def predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Return predicted class labels."""
        self._check_fitted()
        _validate_features(X)
        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Return class probability estimates."""
        self._check_fitted()
        _validate_features(X)
        if not hasattr(self.model, "predict_proba"):
            raise AttributeError(f"{self.algorithm} does not support predict_proba.")
        return self.model.predict_proba(X)

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
        stratify = y if y.nunique() > 1 and y.value_counts().min() > 1 else None
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state, stratify=stratify
        )
        self.model.fit(X_train, y_train)
        self._is_trained = True
        return X_train, X_test, y_train, y_test

    # ── Internals ─────────────────────────────────────────────────────────────

    def _check_fitted(self) -> None:
        if not self._is_trained:
            raise ValueError("Model has not been trained yet. Call train() first.")
