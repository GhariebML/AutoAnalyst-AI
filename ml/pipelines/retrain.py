import pandas as pd
from ..monitoring.drift_detector import DriftDetector
from ..pipelines.training import TrainingPipeline

def run_retrain_check(
    agent_name: str,
    baseline_path: str,
    current_path: str,
    target_col: str,
    numerical_cols: list,
    categorical_cols: list = None
) -> bool:
    """
    Checks for data drift between baseline and current datasets.
    Triggers TrainingPipeline if drift is detected.
    """
    print(f"Checking for data drift in agent '{agent_name}'...")
    
    try:
        baseline_df = pd.read_csv(baseline_path) if baseline_path.endswith('.csv') else pd.read_parquet(baseline_path)
        current_df = pd.read_csv(current_path) if current_path.endswith('.csv') else pd.read_parquet(current_path)
    except Exception as e:
        print(f"Failed to read datasets: {e}. Skipping retrain check.")
        return False

    detector = DriftDetector()
    drift_detected, report = detector.detect_drift(baseline_df, current_df, numerical_cols)

    print(f"Drift report: {report}")
    
    if drift_detected:
        print("Data drift detected! Initiating automatic model retraining...")
        pipeline = TrainingPipeline(
            agent_name=agent_name,
            numerical_cols=numerical_cols,
            categorical_cols=categorical_cols or []
        )
        # Combine baseline and new current data for retraining
        combined_df = pd.concat([baseline_df, current_df], ignore_index=True)
        pipeline.run(combined_df, target_col=target_col)
        print("Retraining complete. New model weights registered.")
        return True
        
    print("No significant data drift detected. Current model remains active.")
    return False
