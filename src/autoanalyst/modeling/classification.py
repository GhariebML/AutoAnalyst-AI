"""Starter classification model wrapper."""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


class ClassificationModel:
    """Simple classification model helper using RandomForestClassifier."""

    def __init__(self, random_state: int = 42) -> None:
        self.model = RandomForestClassifier(random_state=random_state)
        self.random_state = random_state

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
