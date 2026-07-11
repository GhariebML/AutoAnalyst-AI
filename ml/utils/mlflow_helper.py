import os
import mlflow
from typing import Dict, Any, Optional

def setup_mlflow():
    """Initializes local SQLite-backed MLflow tracking server."""
    tracking_db = "sqlite:///mlflow.db"
    mlflow.set_tracking_uri(tracking_db)
    
    # Ensure mlruns directory exists
    os.makedirs("./mlruns", exist_ok=True)
    
def log_experiment(
    experiment_name: str,
    run_name: str,
    params: Dict[str, Any],
    metrics: Dict[str, float],
    artifacts: Optional[list] = None
):
    """Logs parameters, metrics, and artifact files to MLflow."""
    setup_mlflow()
    mlflow.set_experiment(experiment_name)
    
    with mlflow.start_run(run_name=run_name) as run:
        # Log Hyperparameters
        for k, v in params.items():
            mlflow.log_param(k, v)
            
        # Log Metrics
        for k, v in metrics.items():
            mlflow.log_metric(k, v)
            
        # Log Artifacts (e.g. plot images, model cards, csv features)
        if artifacts:
            for artifact_path in artifacts:
                if os.path.exists(artifact_path):
                    mlflow.log_artifact(artifact_path)
                    
        print(f"Logged experiment '{experiment_name}' run '{run_name}' to local MLflow database.")
        return run.info.run_id
