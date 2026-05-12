"""Starter regression model wrapper."""

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split


class RegressionModel:
    """Simple regression model helper using RandomForestRegressor."""

    def __init__(self, random_state: int = 42) -> None:
        self.model = RandomForestRegressor(random_state=random_state)
        self.random_state = random_state

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
