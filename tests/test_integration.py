"""Integration tests for the Machine Learning Engine pipeline."""

import json
import pytest
import numpy as np
import pandas as pd
from ml_engine.integration import run_ml_pipeline


def sample_classification_dataset() -> pd.DataFrame:
    # 10 samples with a categorical feature, numeric feature, and missing values
    return pd.DataFrame({
        "age": [25.0, 30.0, np.nan, 45.0, 35.0, 50.0, 23.0, np.nan, 31.0, 42.0],
        "department": ["HR", "IT", "HR", "Sales", "IT", "Sales", "HR", "IT", np.nan, "Sales"],
        "salary": [50000.0, 70000.0, 48000.0, 85000.0, 68000.0, 95000.0, 45000.0, 62000.0, np.nan, 90000.0],
        "promoted": ["no", "yes", "no", "yes", "no", "yes", "no", "no", "yes", "yes"]
    })


def test_run_ml_pipeline_classification() -> None:
    df = sample_classification_dataset()
    config = {
        "task": "classification",
        "target_column": "promoted",
        "fill_strategy": "median",
        "drop_duplicates": True,
        "outlier_method": None,
        "encode_method": "onehot",
        "scale_method": "standard",
        "algorithm": "random_forest",
        "test_size": 0.3,
        "random_state": 42,
        "stratify": False
    }

    result = run_ml_pipeline(df, config)
    
    assert result["task"] == "classification"
    assert "preprocessed_data_shape" in result
    assert "evaluation_metrics" in result
    assert "accuracy" in result["evaluation_metrics"]
    assert "predictions" in result
    assert "true_values" in result
    assert len(result["predictions"]) == 3 # 10 samples -> duplicates? Let's check duplicates: none. 10 * 0.3 = 3 test rows.
    
    # Verify JSON serializability
    assert json.dumps(result)


def test_run_ml_pipeline_regression() -> None:
    df = sample_classification_dataset()
    config = {
        "task": "regression",
        "target_column": "salary",
        "fill_strategy": "median",
        "drop_duplicates": True,
        "outlier_method": "iqr",
        "encode_method": "label",
        "scale_method": "minmax",
        "algorithm": "linear_regression",
        "test_size": 0.2,
        "random_state": 42
    }

    result = run_ml_pipeline(df, config)
    
    assert result["task"] == "regression"
    assert "evaluation_metrics" in result
    assert "rmse" in result["evaluation_metrics"]
    assert "predictions" in result
    
    # Verify JSON serializability
    assert json.dumps(result)


def test_run_ml_pipeline_clustering() -> None:
    df = sample_classification_dataset()
    # Dropping categorical/object columns for clustering simplicity in test,
    # though our pipeline handles encoding automatically.
    config = {
        "task": "clustering",
        "target_column": "promoted", # Target column should be ignored/dropped from features
        "fill_strategy": "median",
        "drop_duplicates": True,
        "outlier_method": None,
        "encode_method": "onehot",
        "scale_method": "standard",
        "algorithm": "kmeans",
        "hyperparameters": {"n_clusters": 2},
        "random_state": 42
    }

    result = run_ml_pipeline(df, config)
    
    assert result["task"] == "clustering"
    assert "evaluation_metrics" in result
    assert "silhouette_score" in result["evaluation_metrics"]
    assert "cluster_assignments" in result
    assert len(result["cluster_assignments"]) == 10
    
    # Verify JSON serializability
    assert json.dumps(result)


def test_run_ml_pipeline_invalid_config() -> None:
    df = sample_classification_dataset()
    
    # Missing task
    with pytest.raises(ValueError):
        run_ml_pipeline(df, {})
        
    # Invalid task name
    with pytest.raises(ValueError):
        run_ml_pipeline(df, {"task": "invalid_task"})
        
    # Missing target column for classification
    with pytest.raises(ValueError):
        run_ml_pipeline(df, {"task": "classification"})

    # Non-existent target column
    with pytest.raises(KeyError):
        run_ml_pipeline(df, {"task": "classification", "target_column": "nonexistent"})
