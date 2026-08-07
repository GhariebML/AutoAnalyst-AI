"""Model classes wrapping classification, regression, and clustering algorithms."""

import logging
from typing import Any, Literal
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import Lasso, LinearRegression, LogisticRegression, Ridge
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

logger = logging.getLogger(__name__)


def _validate_inputs(X: Any, y: Any = None) -> None:
    """Validate that input data does not contain missing values or non-numeric types."""
    if X is None:
        raise ValueError("Input features (X) cannot be None.")

    if isinstance(X, pd.DataFrame):
        if X.isna().any().any():
            raise ValueError("Input features (X) contain missing values (NaNs). Please impute or drop them.")
        non_numeric = X.select_dtypes(exclude=[np.number]).columns
        if not non_numeric.empty:
            raise ValueError(f"Input features (X) contain non-numeric columns: {list(non_numeric)}. Please encode them.")
    elif isinstance(X, np.ndarray):
        if np.isnan(X).any():
            raise ValueError("Input features (X) contain missing values (NaNs).")
        if not np.issubdtype(X.dtype, np.number):
            raise ValueError("Input features (X) must be numeric.")
    else:
        raise ValueError("Input features (X) must be a pandas DataFrame or a numpy ndarray.")

    if y is not None:
        if isinstance(y, (pd.Series, pd.DataFrame)):
            if y.isna().any().any():
                raise ValueError("Target (y) contains missing values (NaNs). Please impute or drop them.")
        elif isinstance(y, np.ndarray):
            if np.isnan(y).any():
                raise ValueError("Target (y) contains missing values (NaNs).")


class ClassificationModel:
    """Wrapper class for scikit-learn classification models."""

    def __init__(
        self,
        algorithm: Literal["random_forest", "logistic_regression", "svm", "decision_tree"] = "random_forest",
        hyperparameters: dict[str, Any] | None = None,
        random_state: int = 42,
    ) -> None:
        self.algorithm = algorithm.lower()
        self.hyperparameters = hyperparameters or {}
        self.random_state = random_state
        self.model: Any = None
        self._is_trained = False

        self._init_model()

    def _init_model(self) -> None:
        params = self.hyperparameters.copy()

        # Add random_state if supported
        if self.algorithm in {"random_forest", "logistic_regression", "svm", "decision_tree"}:
            if "random_state" not in params and self.algorithm != "linear_regression":
                params["random_state"] = self.random_state

        if self.algorithm == "random_forest":
            self.model = RandomForestClassifier(**params)
        elif self.algorithm == "logistic_regression":
            # Increase max_iter default if not specified to ensure convergence
            if "max_iter" not in params:
                params["max_iter"] = 1000
            self.model = LogisticRegression(**params)
        elif self.algorithm == "svm":
            # Enable probability output for predict_proba
            if "probability" not in params:
                params["probability"] = True
            self.model = SVC(**params)
        elif self.algorithm == "decision_tree":
            self.model = DecisionTreeClassifier(**params)
        else:
            raise ValueError(
                f"Unsupported classification algorithm '{self.algorithm}'. "
                "Must be one of: 'random_forest', 'logistic_regression', 'svm', 'decision_tree'."
            )

    def train(self, X: pd.DataFrame | np.ndarray, y: pd.Series | np.ndarray) -> None:
        """Train the classification model."""
        _validate_inputs(X, y)
        if y is None or len(y) == 0:
            raise ValueError("Target y cannot be empty or None for training.")
        
        self.model.fit(X, y)
        self._is_trained = True
        logger.info(f"Successfully trained {self.algorithm} classification model.")

    def predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Predict labels for the input features."""
        if not self._is_trained:
            raise ValueError("Model is not trained yet. Call train() before predict().")
        _validate_inputs(X)
        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Predict probability estimates for the input features."""
        if not self._is_trained:
            raise ValueError("Model is not trained yet. Call train() before predict_proba().")
        _validate_inputs(X)
        if not hasattr(self.model, "predict_proba"):
            raise AttributeError(f"Model {self.algorithm} does not support probability estimation.")
        return self.model.predict_proba(X)


class RegressionModel:
    """Wrapper class for scikit-learn regression models."""

    def __init__(
        self,
        algorithm: Literal["random_forest", "linear_regression", "ridge", "lasso", "decision_tree"] = "random_forest",
        hyperparameters: dict[str, Any] | None = None,
        random_state: int = 42,
    ) -> None:
        self.algorithm = algorithm.lower()
        self.hyperparameters = hyperparameters or {}
        self.random_state = random_state
        self.model: Any = None
        self._is_trained = False

        self._init_model()

    def _init_model(self) -> None:
        params = self.hyperparameters.copy()

        # Add random_state if supported
        if self.algorithm in {"random_forest", "ridge", "lasso", "decision_tree"}:
            if "random_state" not in params:
                params["random_state"] = self.random_state

        if self.algorithm == "random_forest":
            self.model = RandomForestRegressor(**params)
        elif self.algorithm == "linear_regression":
            self.model = LinearRegression(**params)
        elif self.algorithm == "ridge":
            self.model = Ridge(**params)
        elif self.algorithm == "lasso":
            self.model = Lasso(**params)
        elif self.algorithm == "decision_tree":
            self.model = DecisionTreeRegressor(**params)
        else:
            raise ValueError(
                f"Unsupported regression algorithm '{self.algorithm}'. "
                "Must be one of: 'random_forest', 'linear_regression', 'ridge', 'lasso', 'decision_tree'."
            )

    def train(self, X: pd.DataFrame | np.ndarray, y: pd.Series | np.ndarray) -> None:
        """Train the regression model."""
        _validate_inputs(X, y)
        if y is None or len(y) == 0:
            raise ValueError("Target y cannot be empty or None for training.")
        
        self.model.fit(X, y)
        self._is_trained = True
        logger.info(f"Successfully trained {self.algorithm} regression model.")

    def predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Predict target values for the input features."""
        if not self._is_trained:
            raise ValueError("Model is not trained yet. Call train() before predict().")
        _validate_inputs(X)
        return self.model.predict(X)


class ClusteringModel:
    """Wrapper class for scikit-learn clustering models."""

    def __init__(
        self,
        algorithm: Literal["kmeans", "dbscan", "agglomerative"] = "kmeans",
        hyperparameters: dict[str, Any] | None = None,
        random_state: int = 42,
    ) -> None:
        self.algorithm = algorithm.lower()
        self.hyperparameters = hyperparameters or {}
        self.random_state = random_state
        self.model: Any = None
        self._is_trained = False

        self._init_model()

    def _init_model(self) -> None:
        params = self.hyperparameters.copy()

        # Add random_state if supported
        if self.algorithm == "kmeans":
            if "random_state" not in params:
                params["random_state"] = self.random_state
            if "n_init" not in params:
                params["n_init"] = 10

        if self.algorithm == "kmeans":
            self.model = KMeans(**params)
        elif self.algorithm == "dbscan":
            self.model = DBSCAN(**params)
        elif self.algorithm == "agglomerative":
            self.model = AgglomerativeClustering(**params)
        else:
            raise ValueError(
                f"Unsupported clustering algorithm '{self.algorithm}'. "
                "Must be one of: 'kmeans', 'dbscan', 'agglomerative'."
            )

    def train_predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Train the model and return cluster labels for the training set."""
        _validate_inputs(X)
        labels = self.model.fit_predict(X)
        self._is_trained = True
        logger.info(f"Successfully fit {self.algorithm} clustering model.")
        return labels

    def predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Predict clusters for new data. Only supported for algorithms that allow inductive inference (e.g. KMeans)."""
        if not self._is_trained:
            raise ValueError("Model is not trained yet. Call train_predict() before predict().")
        _validate_inputs(X)
        
        if hasattr(self.model, "predict"):
            return self.model.predict(X)
        else:
            raise ValueError(
                f"Algorithm '{self.algorithm}' does not support prediction on new data. "
                "Only inductive methods like 'kmeans' support predict()."
            )
