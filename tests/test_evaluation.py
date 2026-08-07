"""Unit tests for the evaluation module."""

import json
import pytest
import numpy as np
from ml_engine.evaluation import evaluate_classification, evaluate_regression, evaluate_clustering


def test_evaluate_classification_binary() -> None:
    y_true = [0, 1, 0, 1, 0, 1]
    y_pred = [0, 1, 0, 0, 0, 1] # 5 out of 6 correct, accuracy = 5/6
    y_prob = [0.1, 0.9, 0.2, 0.4, 0.3, 0.85]

    metrics = evaluate_classification(y_true, y_pred, y_prob=y_prob)
    
    assert metrics["accuracy"] == pytest.approx(5 / 6)
    assert "precision_macro" in metrics
    assert "f1_weighted" in metrics
    assert metrics["roc_auc"] is not None
    assert isinstance(metrics["confusion_matrix"], list)
    
    # Check JSON serializability
    serialized = json.dumps(metrics)
    assert serialized


def test_evaluate_classification_multiclass() -> None:
    y_true = [0, 1, 2, 0, 1, 2]
    y_pred = [0, 1, 2, 0, 2, 1]
    # probabilities for 3 classes
    y_prob = [
        [0.8, 0.1, 0.1],
        [0.1, 0.8, 0.1],
        [0.1, 0.1, 0.8],
        [0.7, 0.2, 0.1],
        [0.2, 0.3, 0.5],
        [0.2, 0.6, 0.2]
    ]

    metrics = evaluate_classification(y_true, y_pred, y_prob=y_prob)
    assert metrics["accuracy"] == pytest.approx(4 / 6)
    assert metrics["roc_auc"] is not None
    
    # Check JSON serializability
    serialized = json.dumps(metrics)
    assert serialized


def test_evaluate_regression() -> None:
    y_true = [1.0, 2.0, 3.0]
    y_pred = [1.1, 1.9, 3.1]

    metrics = evaluate_regression(y_true, y_pred)
    assert metrics["mse"] == pytest.approx(0.01)
    assert metrics["rmse"] == pytest.approx(0.1)
    assert metrics["mae"] == pytest.approx(0.1)
    assert "r2" in metrics

    # Check JSON serializability
    serialized = json.dumps(metrics)
    assert serialized


def test_evaluate_clustering_valid() -> None:
    X = [
        [1.0, 1.0],
        [1.1, 1.0],
        [5.0, 5.0],
        [5.1, 5.0]
    ]
    labels = [0, 0, 1, 1]

    metrics = evaluate_clustering(X, labels)
    assert metrics["n_clusters"] == 2
    assert metrics["silhouette_score"] is not None
    assert metrics["silhouette_score"] > 0.5
    assert metrics["davies_bouldin_index"] is not None
    
    # Check JSON serializability
    serialized = json.dumps(metrics)
    assert serialized


def test_evaluate_clustering_edge_case() -> None:
    # Less than 2 clusters (all 0 or all -1 noise)
    X = [
        [1.0, 1.0],
        [1.1, 1.0],
        [5.0, 5.0]
    ]
    
    # All same label
    labels_single = [0, 0, 0]
    metrics_single = evaluate_clustering(X, labels_single)
    assert metrics_single["silhouette_score"] is None
    assert metrics_single["davies_bouldin_index"] is None
    assert metrics_single["n_clusters"] == 1
    
    # All noise labels
    labels_noise = [-1, -1, -1]
    metrics_noise = evaluate_clustering(X, labels_noise)
    assert metrics_noise["silhouette_score"] is None
    assert metrics_noise["n_clusters"] == 0
    assert metrics_noise["noise_count"] == 3


def test_evaluate_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        evaluate_classification([1], [1, 2])
    with pytest.raises(ValueError):
        evaluate_regression([1], [1, 2])
    with pytest.raises(ValueError):
        evaluate_clustering([[1, 2]], [1, 2])
