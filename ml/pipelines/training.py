import os
import pickle
from typing import Tuple, Dict, Any
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, Ridge

from ..configs.config import load_agent_config, AgentMLConfig
from ..preprocessing.processor import DataCleaner, FeatureTransformer

class TrainingPipeline:
    """Production training pipeline for executing model fitting and optimization."""

    def __init__(self, agent_name: str, numerical_cols: list, categorical_cols: list = None):
        self.agent_name = agent_name
        self.config: AgentMLConfig = load_agent_config(agent_name)
        self.transformer = FeatureTransformer(numerical_cols, categorical_cols or [])

    def _select_model(self) -> Any:
        """Instantiates the candidate model based on algorithm configuration."""
        algo = self.config.model.algorithm.lower()
        params = self.config.model.hyperparameters
        
        # Classification models
        if algo == "random_forest":
            return RandomForestClassifier(random_state=self.config.data.random_state, **params)
        elif algo == "logistic_regression":
            return LogisticRegression(random_state=self.config.data.random_state, **params)
            
        # Regression models
        elif algo == "random_forest_regressor":
            return RandomForestRegressor(random_state=self.config.data.random_state, **params)
        elif algo == "ridge":
            return Ridge(random_state=self.config.data.random_state, **params)
            
        else:
            raise ValueError(f"Unsupported algorithm: {algo}")

    def run(self, df: pd.DataFrame, target_col: str) -> Pipeline:
        """Cleans, preprocesses, splits, fits, and registers the model."""
        df_clean = DataCleaner.clean(df)
        
        X = df_clean.drop(target_col, axis=1)
        y = df_clean[target_col]
        
        # Split (Support chronological split for time-series, stratified for classification)
        is_classification = self.config.model.algorithm.lower() in ["random_forest", "logistic_regression"]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=self.config.data.test_size,
            random_state=self.config.data.random_state,
            shuffle=is_classification, # Shuffle for classification, chronological order for time-series
            stratify=y if is_classification else None
        )
        
        # Preprocessor & Pipeline
        preprocessor = self.transformer.preprocessor
        model = self._select_model()
        
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('model', model)
        ])
        
        # Fit Model
        pipeline.fit(X_train, y_train)
        
        # Save Model to Registry
        registry_dir = "ml/registry"
        os.makedirs(registry_dir, exist_ok=True)
        model_path = os.path.join(registry_dir, f"{self.agent_name}_model.pkl")
        
        with open(model_path, "wb") as f:
            pickle.dump(pipeline, f)
            
        print(f"Successfully trained and saved model for {self.agent_name} to {model_path}")

        # Compute Metrics for MLflow Logging
        y_pred = pipeline.predict(X_test)
        metrics = {}
        if is_classification:
            from sklearn.metrics import f1_score, accuracy_score
            metrics["f1_score"] = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
            metrics["accuracy"] = float(accuracy_score(y_test, y_pred))
        else:
            from sklearn.metrics import mean_absolute_error, mean_squared_error
            metrics["mae"] = float(mean_absolute_error(y_test, y_pred))
            metrics["rmse"] = float(mean_squared_error(y_test, y_pred) ** 0.5)

        # Log Run to MLflow
        try:
            from ..utils.mlflow_helper import log_experiment
            log_experiment(
                experiment_name=f"{self.agent_name}_experiment",
                run_name="train_run",
                params=self.config.model.hyperparameters,
                metrics=metrics,
                artifacts=[model_path]
            )
        except Exception as e:
            print(f"Failed to log experiment to MLflow: {e}")

        return pipeline
