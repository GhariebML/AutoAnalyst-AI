"""Unit tests for the models module."""

import pytest
import numpy as np
import pandas as pd
from ml_engine.models import ClassificationModel, RegressionModel, ClusteringModel


def test_classification_model_random_forest() -> None:
    X = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0], "b": [2.0, 3.0, 1.0, 5.0, 4.0, 6.0]})
    y = pd.Series([0, 0, 0, 1, 1, 1])

    clf = ClassificationModel(algorithm="random_forest", random_state=42)
    clf.train(X, y)
    preds = clf.predict(X)
    assert len(preds) == len(y)
    
    probs = clf.predict_proba(X)
    assert probs.shape == (len(y), 2)


def test_classification_model_logistic_regression() -> None:
    X = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0], "b": [1.1, 1.9, 3.2, 3.8]})
    y = pd.Series([0, 0, 1, 1])

    clf = ClassificationModel(algorithm="logistic_regression", random_state=42)
    clf.train(X, y)
    preds = clf.predict(X)
    assert len(preds) == len(y)


def test_classification_model_svm() -> None:
    X = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0], "b": [1.1, 1.9, 3.2, 3.8]})
    y = pd.Series([0, 0, 1, 1])

    clf = ClassificationModel(algorithm="svm", random_state=42)
    clf.train(X, y)
    preds = clf.predict(X)
    probs = clf.predict_proba(X)
    assert len(preds) == len(y)
    assert probs.shape == (len(y), 2)


def test_classification_model_decision_tree() -> None:
    X = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0], "b": [1.1, 1.9, 3.2, 3.8]})
    y = pd.Series([0, 0, 1, 1])

    clf = ClassificationModel(algorithm="decision_tree", random_state=42)
    clf.train(X, y)
    preds = clf.predict(X)
    assert len(preds) == len(y)


def test_classification_model_validation() -> None:
    X_missing = pd.DataFrame({"a": [1.0, np.nan], "b": [2.0, 3.0]})
    y = pd.Series([0, 1])
    clf = ClassificationModel(algorithm="random_forest")
    
    # Missing values check
    with pytest.raises(ValueError):
        clf.train(X_missing, y)
        
    # Non-numeric values check
    X_non_numeric = pd.DataFrame({"a": ["high", "low"], "b": [2.0, 3.0]})
    with pytest.raises(ValueError):
        clf.train(X_non_numeric, y)

    # Predict before train check
    X_valid = pd.DataFrame({"a": [1.0, 2.0], "b": [2.0, 3.0]})
    with pytest.raises(ValueError):
        clf.predict(X_valid)


def test_regression_model() -> None:
    X = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0], "b": [10.0, 20.0, 30.0, 40.0]})
    y = pd.Series([1.5, 2.5, 3.5, 4.5])

    for algo in ["linear_regression", "random_forest", "ridge", "lasso", "decision_tree"]:
        reg = RegressionModel(algorithm=algo, random_state=42)
        reg.train(X, y)
        preds = reg.predict(X)
        assert len(preds) == len(y)


def test_clustering_model_kmeans() -> None:
    X = pd.DataFrame({"a": [1.0, 1.1, 5.0, 5.2], "b": [1.0, 0.9, 5.0, 4.8]})

    kmeans = ClusteringModel(algorithm="kmeans", hyperparameters={"n_clusters": 2}, random_state=42)
    labels = kmeans.train_predict(X)
    assert len(labels) == len(X)
    assert len(np.unique(labels)) == 2
    
    # KMeans supports predicting on new data
    preds = kmeans.predict(X)
    assert np.array_equal(labels, preds)


def test_clustering_model_dbscan() -> None:
    X = pd.DataFrame({"a": [1.0, 1.1, 5.0, 5.2], "b": [1.0, 0.9, 5.0, 4.8]})

    dbscan = ClusteringModel(algorithm="dbscan", hyperparameters={"eps": 1.5, "min_samples": 2})
    labels = dbscan.train_predict(X)
    assert len(labels) == len(X)
    
    # DBSCAN does not support predict on new data
    with pytest.raises(ValueError):
        dbscan.predict(X)


def test_clustering_model_invalid_algo() -> None:
    with pytest.raises(ValueError):
        ClusteringModel(algorithm="invalid_clustering_algo")  # type: ignore
