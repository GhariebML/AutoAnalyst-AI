"""Clustering model wrapper — Team 5 (NEW file)."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans

logger = logging.getLogger(__name__)

_SUPPORTED_ALGORITHMS = frozenset({"kmeans", "dbscan", "agglomerative"})


def _validate_features(X: Any) -> None:
    if isinstance(X, pd.DataFrame):
        bad = list(X.select_dtypes(exclude=[np.number, bool, "bool", "boolean"]).columns)
        if bad:
            raise ValueError(f"Features contain non-numeric columns: {bad}.")
        if X.isna().any().any():
            raise ValueError("Features contain NaN values. Impute them first.")
    elif isinstance(X, np.ndarray):
        if np.isnan(X).any():
            raise ValueError("Features contain NaN values.")


class ClusteringModel:
    """Unified wrapper around scikit-learn clustering estimators.

    Parameters
    ----------
    algorithm:
        One of ``'kmeans'``, ``'dbscan'``, ``'agglomerative'``.
    hyperparameters:
        Optional estimator keyword arguments.
    random_state:
        Random seed (forwarded to KMeans / AgglomerativeClustering).
    """

    def __init__(
        self,
        algorithm: str = "kmeans",
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

        if algo == "kmeans":
            hp.setdefault("n_clusters", 3)
            hp.setdefault("random_state", random_state)
            hp.setdefault("n_init", 10)
            self.model: Any = KMeans(**hp)
        elif algo == "dbscan":
            hp.setdefault("eps", 0.5)
            hp.setdefault("min_samples", 5)
            self.model = DBSCAN(**hp)
        elif algo == "agglomerative":
            hp.setdefault("n_clusters", 3)
            self.model = AgglomerativeClustering(**hp)

    # ── Public methods ────────────────────────────────────────────────────────

    def train_predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Fit and return cluster label assignments."""
        _validate_features(X)
        labels: np.ndarray = self.model.fit_predict(X)
        self._is_trained = True
        n_clusters = int(len(np.unique(labels[labels != -1])))
        logger.info(
            "ClusteringModel (%s) fitted — %d clusters found.",
            self.algorithm, n_clusters,
        )
        return labels

    def predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Predict clusters for new samples (KMeans only)."""
        if not self._is_trained:
            raise ValueError("Call train_predict() before predict().")
        if not hasattr(self.model, "predict"):
            raise AttributeError(
                f"'{self.algorithm}' does not support inductive prediction. "
                "Use KMeans for out-of-sample prediction."
            )
        _validate_features(X)
        return self.model.predict(X)
