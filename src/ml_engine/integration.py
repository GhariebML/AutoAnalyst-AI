"""Integration layer to run the machine learning pipeline end-to-end."""

import logging
from typing import Any, Literal
import numpy as np
import pandas as pd

from ml_engine.evaluation import evaluate_classification, evaluate_clustering, evaluate_regression
from ml_engine.models import ClassificationModel, ClusteringModel, RegressionModel
from ml_engine.preprocessing import clean_data, encode_features, scale_features, split_data

logger = logging.getLogger(__name__)


def run_ml_pipeline(df: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    """Run the end-to-end ML pipeline: preprocessing, modeling, and evaluation.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    config : dict
        Pipeline configuration options:
        - "task": {"classification", "regression", "clustering"} (Required)
        - "target_column": str (Required for classification and regression)
        - "fill_strategy": str or dict (Default: "median")
        - "drop_duplicates": bool (Default: True)
        - "outlier_method": {"iqr", "z_score"} or None (Default: None)
        - "encode_method": {"onehot", "label"} (Default: "onehot")
        - "scale_method": {"standard", "minmax"} (Default: "standard")
        - "algorithm": str (Default dependent on task: e.g. "random_forest" or "kmeans")
        - "hyperparameters": dict (Default: None)
        - "test_size": float (Default: 0.2)
        - "random_state": int (Default: 42)
        - "stratify": bool (Default: False)

    Returns
    -------
    dict
        A JSON-serializable dictionary containing pipeline metrics, parameters,
        and predictions.
    """
    if df is None:
        raise ValueError("DataFrame cannot be None.")
    if config is None:
        raise ValueError("Configuration dictionary cannot be None.")
    
    # 1. Configuration Validation
    task = config.get("task")
    if task not in {"classification", "regression", "clustering"}:
        raise ValueError("Config 'task' must be 'classification', 'regression', or 'clustering'.")
    
    target_col = config.get("target_column")
    if task in {"classification", "regression"} and not target_col:
        raise ValueError(f"Config 'target_column' is required for '{task}' task.")

    if target_col and target_col not in df.columns:
        raise KeyError(f"Target column '{target_col}' not found in the input DataFrame.")

    random_state = config.get("random_state", 42)
    test_size = config.get("test_size", 0.2)
    
    # 2. Data Cleaning
    cleaned_df = clean_data(
        df=df,
        fill_strategy=config.get("fill_strategy", "median"),
        drop_duplicates=config.get("drop_duplicates", True),
        outlier_method=config.get("outlier_method", None),
    )

    if cleaned_df.empty:
        raise ValueError("The DataFrame is empty after data cleaning.")

    # 3. Separate features and target if supervised
    if task in {"classification", "regression"}:
        # In case target column was dropped during duplicate/null cleanings
        if target_col not in cleaned_df.columns:
            raise KeyError(f"Target column '{target_col}' was dropped or is missing after cleaning.")
            
        X = cleaned_df.drop(columns=[target_col])
        y = cleaned_df[target_col]
    else:
        # For clustering, drop the target column if it was specified
        if target_col and target_col in cleaned_df.columns:
            X = cleaned_df.drop(columns=[target_col])
        else:
            X = cleaned_df.copy()
        y = None

    # 4. Feature Encoding and Scaling
    # Encode categorical columns
    X_encoded = encode_features(
        X,
        categorical_cols=None,
        method=config.get("encode_method", "onehot"),
    )
    
    # Scale numeric columns
    X_scaled = scale_features(
        X_encoded,
        numeric_cols=None,
        method=config.get("scale_method", "standard"),
    )

    # 5. Modeling and Evaluation
    result: dict[str, Any] = {
        "task": task,
        "config": {
            "algorithm": config.get("algorithm", "random_forest" if task != "clustering" else "kmeans"),
            "hyperparameters": config.get("hyperparameters", {}),
            "random_state": random_state,
        },
    }

    if task == "classification":
        # Prepare data for splitting
        df_model_ready = X_scaled.copy()
        df_model_ready[target_col] = y
        
        X_train, X_test, y_train, y_test = split_data(
            df_model_ready,
            target_col=target_col,
            test_size=test_size,
            random_state=random_state,
            stratify=config.get("stratify", False),
        )

        algo = config.get("algorithm", "random_forest")
        model = ClassificationModel(
            algorithm=algo,
            hyperparameters=config.get("hyperparameters"),
            random_state=random_state,
        )
        
        model.train(X_train, y_train)
        y_pred = model.predict(X_test)
        
        y_prob = None
        if hasattr(model.model, "predict_proba"):
            try:
                y_prob = model.predict_proba(X_test)
            except Exception:
                pass
                
        eval_metrics = evaluate_classification(y_test, y_pred, y_prob=y_prob)
        
        result.update({
            "preprocessed_data_shape": {
                "train_features": X_train.shape,
                "test_features": X_test.shape,
            },
            "evaluation_metrics": eval_metrics,
            "predictions": y_pred.tolist(),
            "true_values": y_test.tolist(),
        })

    elif task == "regression":
        # Prepare data for splitting
        df_model_ready = X_scaled.copy()
        df_model_ready[target_col] = y
        
        X_train, X_test, y_train, y_test = split_data(
            df_model_ready,
            target_col=target_col,
            test_size=test_size,
            random_state=random_state,
            stratify=False,
        )

        algo = config.get("algorithm", "random_forest")
        model = RegressionModel(
            algorithm=algo,
            hyperparameters=config.get("hyperparameters"),
            random_state=random_state,
        )
        
        model.train(X_train, y_train)
        y_pred = model.predict(X_test)
        
        eval_metrics = evaluate_regression(y_test, y_pred)
        
        result.update({
            "preprocessed_data_shape": {
                "train_features": X_train.shape,
                "test_features": X_test.shape,
            },
            "evaluation_metrics": eval_metrics,
            "predictions": y_pred.tolist(),
            "true_values": y_test.tolist(),
        })

    elif task == "clustering":
        algo = config.get("algorithm", "kmeans")
        model = ClusteringModel(
            algorithm=algo,
            hyperparameters=config.get("hyperparameters"),
            random_state=random_state,
        )
        
        labels = model.train_predict(X_scaled)
        eval_metrics = evaluate_clustering(X_scaled, labels)
        
        result.update({
            "preprocessed_data_shape": {
                "features": X_scaled.shape,
            },
            "evaluation_metrics": eval_metrics,
            "cluster_assignments": labels.tolist(),
        })

    return result
