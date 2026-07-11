# AdPilot Pro – Data & Modeling Standards

This document establishes standard dataset layouts, coding conventions, configuration guidelines, and deployment strategies for the machine learning architecture.

---

## 📂 1. ML Folder Structure

The machine learning assets are organized under a top-level `ml/` folder in the project workspace, keeping model code isolated from API and client UI code:

```text
ml/
├── configs/                  # YAML configurations for models and training runs
├── datasets/                 # Local directory for raw, interim, and processed data
│   ├── raw/                  # Unmodified source datasets
│   ├── interim/              # Preprocessed data undergoing transformations
│   └── processed/            # Final features ready for model ingestion
├── notebooks/                # Jupyter Notebooks for EDA and model validation
├── preprocessing/            # Ingestion, cleaning, and normalization modules
├── feature_engineering/      # Feature store loaders and feature extraction scripts
├── models/                   # Python classes defining custom models and wrappers
├── training/                 # Script runners to trigger batch training
├── evaluation/               # Model comparison, SHAP analysis, and metrics logging
├── inference/                # Real-time predictor classes integrated with agents
├── experiments/              # Local mlflow tracking files and metadata databases
├── registry/                 # Offline model checkpoints and model card artifacts
├── pipelines/                # Full training/inference pipeline orchestration
├── monitoring/               # Data drift detection and performance monitoring scripts
└── utils/                    # Common helper modules, decorators, and loggers
```

---

## 🏷️ 2. Naming Conventions & Code Standards

To keep the codebase maintainable, all ML elements follow standard naming guidelines:

* **Notebooks**: Prefix with index matching pipeline order. E.g., `ml/notebooks/01_strategy_pipeline.ipynb`.
* **Config Files**: Name matches the agent ID. E.g., `ml/configs/strategy.yaml`.
* **Model Artifacts (MLflow)**: Standard name matching the pattern `<agent_id>_model`. E.g., `strategy_model`.
* **Model Versions**: Registered models use semantic tags: `Staging` (candidate models under test), `Production` (active models in service).

---

## ⚙️ 3. Configuration Strategy

Model parameters, training details, paths, and environment settings are kept in YAML files under `ml/configs/` and parsed using Pydantic Settings.

### Example configuration (`ml/configs/strategy.yaml`):
```yaml
model:
  name: strategy_model
  algorithm: lightgbm
  hyperparameters:
    learning_rate: 0.05
    n_estimators: 150
    max_depth: 6
    num_leaves: 31

data:
  raw_path: ml/datasets/raw/strategy_data.csv
  processed_path: ml/datasets/processed/strategy_features.parquet
  test_size: 0.2
  random_state: 42

evaluation:
  target_metrics:
    accuracy: 0.82
    f1_macro: 0.80
```

---

## 🔬 4. Evaluation Strategy

To prevent model regression and data leakage:
1. **Splitting Pattern**: Time-based split is enforced for forecast/time-series data. Stratified split is used for classification.
2. **Standard Metrics**:
   * *Classification*: Precision, Recall, F1-Score, ROC-AUC, Log Loss, and Confusion Matrix.
   * *Regression/Forecast*: Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and R² Score.
3. **Threshold Gate**: No model can be promoted to `Production` in the Model Registry unless it outperforms the current production baseline on the test dataset.

---

## 🚀 5. Deployment Strategy

* **Execution Context**: Models are loaded directly into the FastAPI application process on startup via the dependency injection `Container` service, preventing networking overhead during local testing.
* **Warm-up**: Models perform a single dummy inference run on startup to warm up memory and confirm that model weights are loaded correctly.
* **Fallback Mode**: In the event of model loading or inference failure, the API catches exceptions and switches to a deterministic business-rule fallback to guarantee 100% liveness of the dashboard.
