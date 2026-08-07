# Machine Learning Engine Module Documentation

This documentation provides details on the Machine Learning Engine (`ml_engine`) module built for the `AutoAnalyst-AI` project.

---

## 1. Overview & Directory Layout

The Machine Learning Engine is responsible for automated preprocessing, model training, evaluation, and end-to-end orchestration. It is designed to consume raw or partially cleaned pandas DataFrames and produce fully validated models with JSON-serializable evaluation statistics.

The module files are organized as follows:

```
src/ml_engine/
├── __init__.py           # Exports public API interfaces
├── preprocessing.py      # Cleans, encodes, scales, and splits data
├── models.py             # Wraps scikit-learn classification, regression, and clustering algorithms
├── evaluation.py         # Computes JSON-serializable model performance metrics
└── integration.py        # Orchestrates the E2E ML pipeline

tests/
├── test_preprocessing.py # Unit tests for data preprocessing
├── test_models.py        # Unit tests for classification, regression, clustering models
├── test_evaluation.py    # Unit tests for metrics correctness and serializability
└── test_integration.py   # Integration tests for end-to-end run_ml_pipeline
```

---

## 2. Dependencies

The module relies on the following libraries installed from the project's `requirements.txt`:
* **pandas** (>= 2.2.0)
* **numpy** (>= 1.26.0)
* **scikit-learn** (>= 1.4.0)
* **pytest** (>= 8.0.0)

---

## 3. Module APIs

### Preprocessing (`ml_engine.preprocessing`)

Provides data transformation utilities.

* **`clean_data(df, fill_strategy='median', drop_duplicates=True, outlier_method=None)`**
  * *Purpose*: Handles duplicates, drops/imputes missing values (mean, median, mode, constant), and handles outliers using either Interquartile Range (IQR) or Z-score based clipping.
  * *Returns*: `pd.DataFrame`

* **`encode_features(df, categorical_cols=None, method='onehot')`**
  * *Purpose*: Encodes categorical features to numeric representations.
  * *Methods*: `"onehot"` (produces binary column indicators) or `"label"` (produces integer category IDs).
  * *Returns*: `pd.DataFrame`

* **`scale_features(df, numeric_cols=None, method='standard')`**
  * *Purpose*: Standardizes (`StandardScaler`) or normalizes (`MinMaxScaler`) numerical features.
  * *Returns*: `pd.DataFrame`

* **`split_data(df, target_col, test_size=0.2, random_state=42, stratify=False)`**
  * *Purpose*: Splitting target column from features and dividing into train/test sets. Correctly handles class-frequency stratification checks to prevent downstream split errors.
  * *Returns*: `(X_train, X_test, y_train, y_test)`

---

### Models (`ml_engine.models`)

Wraps scikit-learn models under a standardized interface with built-in validation guards against invalid data (like non-numeric features or missing NaNs).

* **`ClassificationModel`**
  * *Algorithms*: `"random_forest"`, `"logistic_regression"`, `"svm"`, `"decision_tree"`
  * *APIs*:
    * `train(X, y)`: Fits the model.
    * `predict(X)`: Generates class predictions.
    * `predict_proba(X)`: Generates prediction probabilities (supports SVM, Random Forest, and Logistic Regression).

* **`RegressionModel`**
  * *Algorithms*: `"random_forest"`, `"linear_regression"`, `"ridge"`, `"lasso"`, `"decision_tree"`
  * *APIs*:
    * `train(X, y)`: Fits the model.
    * `predict(X)`: Generates continuous numeric predictions.

* **`ClusteringModel`**
  * *Algorithms*: `"kmeans"`, `"dbscan"`, `"agglomerative"`
  * *APIs*:
    * `train_predict(X)`: Fits clustering and returns the label assignments.
    * `predict(X)`: Performs inductive clustering prediction on new data (supported only for `"kmeans"`).

---

### Evaluation (`ml_engine.evaluation`)

Computes validation metrics, ensuring that all NumPy-specific datatypes are transformed to standard Python equivalents for reliable JSON serialization.

* **`evaluate_classification(y_true, y_pred, y_prob=None)`**
  * *Metrics*: Accuracy, Macro Precision/Recall/F1, Weighted Precision/Recall/F1, Confusion Matrix (as a list of lists), classification report dict, and ROC-AUC (when `y_prob` is provided).

* **`evaluate_regression(y_true, y_pred)`**
  * *Metrics*: Mean Squared Error (MSE), Root Mean Squared Error (RMSE), Mean Absolute Error (MAE), and Coefficient of Determination (R²).

* **`evaluate_clustering(X, labels)`**
  * *Metrics*: Silhouette Score, Davies-Bouldin Index, cluster counts, and noise count. Safely handles edge cases like a single cluster assignment or DBSCAN noise-only datasets by yielding `None` for metrics rather than crashing.

---

### Integration (`ml_engine.integration`)

Orchestrates the individual steps of the machine learning lifecycle.

* **`run_ml_pipeline(df, config)`**
  * *Parameters*:
    * `df`: The raw `pd.DataFrame`.
    * `config`: Dictionary specifying pipeline instructions:
      ```python
      config = {
          "task": "classification",      # "classification", "regression", or "clustering"
          "target_column": "promoted",   # Required for classification/regression
          "fill_strategy": "median",     # Imputation strategy
          "drop_duplicates": True,
          "outlier_method": None,        # "iqr", "z_score", or None
          "encode_method": "onehot",     # "onehot" or "label"
          "scale_method": "standard",    # "standard" or "minmax"
          "algorithm": "random_forest",  # Desired model algorithm
          "hyperparameters": {},         # Custom model parameters
          "test_size": 0.2,
          "random_state": 42,
          "stratify": False
      }
      ```
  * *Returns*: A standardized dictionary containing the task type, used configurations, preprocessing shapes, predictions, actual values, and evaluation metrics.

---

## 4. Usage Example

```python
import pandas as pd
from ml_engine.integration import run_ml_pipeline

# 1. Load your dataset
df = pd.read_csv("data/employees.csv")

# 2. Setup your configuration
config = {
    "task": "classification",
    "target_column": "promoted",
    "fill_strategy": "median",
    "outlier_method": "iqr",
    "encode_method": "onehot",
    "scale_method": "standard",
    "algorithm": "random_forest",
    "test_size": 0.2,
    "random_state": 42,
    "stratify": True
}

# 3. Run the end-to-end pipeline
result = run_ml_pipeline(df, config)

# 4. View results
print(f"Test Accuracy: {result['evaluation_metrics']['accuracy']:.4f}")
print(f"Predictions: {result['predictions'][:10]}")
```

---

## 5. Testing & Verification

All modules have comprehensive tests located in the `tests/` directory.

To run the full suite of unit and integration tests, use the Python interpreter to execute pytest in the workspace root:

```powershell
python -m pytest tests/test_preprocessing.py tests/test_models.py tests/test_evaluation.py tests/test_integration.py -v
```

To run all tests in the repository (including pipeline integration tests):
```powershell
python -m pytest
```
