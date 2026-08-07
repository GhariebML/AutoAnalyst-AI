"""Machine Learning Engine module for AutoAnalyst AI.

This module provides data preprocessing, machine learning models,
evaluation metrics, and end-to-end integration capabilities.
"""

from ml_engine.preprocessing import clean_data, encode_features, scale_features, split_data
from ml_engine.models import ClassificationModel, RegressionModel, ClusteringModel
from ml_engine.evaluation import evaluate_classification, evaluate_regression, evaluate_clustering
from ml_engine.integration import run_ml_pipeline

__all__ = [
    "clean_data",
    "encode_features",
    "scale_features",
    "split_data",
    "ClassificationModel",
    "RegressionModel",
    "ClusteringModel",
    "evaluate_classification",
    "evaluate_regression",
    "evaluate_clustering",
    "run_ml_pipeline",
]
