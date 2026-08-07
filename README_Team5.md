# Team 5: Machine Learning Engine - AutoAnalyst AI

This repository contains the documentation and implementation details for the **Machine Learning Engine** module developed by **Team 5**. Team 5 is fully responsible for the design, development, testing, integration, and delivery of this predictive model training stage of the AutoAnalyst AI project.

## Team Members
* **Mohamed Khaled El-Shayep** (Team Leader)
* **Mahmoud Maher**

---

## Module Overview & Responsibilities

The Machine Learning Engine (`ml_engine`) serves as the predictive modeling core of the AutoAnalyst AI application. It is responsible for transforming cleaned input datasets, configuring and training classification, regression, and clustering algorithms, computing robust performance metrics, and orchestrating these functions into an integrated pipeline.

### Core Tasks
1. **Data Preprocessing**:
   * Outlier detection and clipping (via IQR or Z-score).
   * Data cleaning (duplicate removal, and missing values imputation with fallback mode handling for non-numeric columns).
   * Feature scaling (Standard and Min-Max scaling).
   * Categorical feature encoding (One-Hot and Label encoding).
   * Stratified train-test splitting for classification tasks.
2. **Model Development**:
   * Classification models: Logistic Regression, Random Forest, SVM, and Decision Trees.
   * Regression models: Linear Regression, Random Forest, Ridge, Lasso, and Decision Trees.
   * Clustering models: K-Means, DBSCAN, and Agglomerative Clustering.
3. **Model Evaluation**:
   * Structured performance metrics (Accuracy, Precision, Recall, F1-scores, Confusion Matrix, MSE, RMSE, MAE, R², Silhouette Score, Davies-Bouldin Index).
   * Native Python type coercion to ensure all outputs are fully JSON-serializable.
4. **Pipeline Integration**:
   * Orchestration helper `run_ml_pipeline` to automate preprocessing, training, prediction, and evaluation.
5. **Testing**:
   * Unit and integration test suites running under pytest.
6. **Documentation**:
   * Clear instruction markdown files describing usage and configuration options.

---

## File Structure

```
src/ml_engine/
├── __init__.py           # Package initialization & public API exports
├── preprocessing.py      # Imputation, outlier handling, scaling, encoding, and splits
├── models.py             # Classification, regression, and clustering model wrappers
├── evaluation.py         # Performance metric calculators
└── integration.py        # Pipeline orchestration layer

tests/
├── test_preprocessing.py # Unit tests for preprocessing operations
├── test_models.py        # Unit tests for model fit-predict flows
├── test_evaluation.py    # Unit tests for performance metrics correctness
└── test_integration.py   # Integration tests for run_ml_pipeline

docs/
└── ml_engine_documentation.md # Exhaustive API documentation and examples
```

---

## Tools & Libraries Used

The Machine Learning Engine is built in Python (>=3.10) and leverages the following standard dependencies:
* **pandas** (>= 2.2.0) - For tabular data structures and data manipulation.
* **numpy** (>= 1.26.0) - For numerical array manipulation and vector calculations.
* **scikit-learn** (>= 1.4.0) - For machine learning algorithms, preprocessing transformations, and evaluation metrics.
* **matplotlib** (>= 3.8.0) & **seaborn** (>= 0.13.0) & **plotly** (>= 5.20.0) - For visualization functions.
* **streamlit** (>= 1.33.0) - For visual dashboard rendering.
* **openpyxl** (>= 3.1.0) - For Excel workbook parsing.
* **pytest** (>= 8.0.0) - For running unit and integration tests.

---

## Implementation Phases & Deliverables

1. **Phase 1: Environment Setup**: Configured Python environments, validated library installs from `requirements.txt`.
2. **Phase 2: Package Structure Creation**: Formed directory structures and set up public API imports in `__init__.py`.
3. **Phase 3: Preprocessing Logic Implementation**: Built data cleaning, outlier handling, category encoding, numeric scaling, and stratified splitting logic.
4. **Phase 4: Model Wrappers Development**: Created classification, regression, and clustering wrappers around scikit-learn models with input validations.
5. **Phase 5: Evaluation Engine Design**: Coded performance metric functions that produce JSON-serializable outputs.
6. **Phase 6: Orchestration Integration**: Created the `run_ml_pipeline` integration entry-point.
7. **Phase 7: Test Coverage**: Created unit and integration test modules under `tests/`.
8. **Phase 8: Documentation**: Created `docs/ml_engine_documentation.md` and this team README.
9. **Phase 9: Verification**: Verified pipeline compilation and executed tests using pytest.
10. **Phase 10: Code Delivery**: Frozen module ready for pipeline consumption by other teams.

---

## Usage Example

The following code snippet demonstrates how to configure and execute the E2E Machine Learning pipeline:

```python
import pandas as pd
from ml_engine.integration import run_ml_pipeline

# 1. Prepare raw training data
data = {
    "age": [24.0, 31.0, None, 45.0, 35.0, 50.0, 23.0, 38.0, 31.0, 42.0],
    "department": ["HR", "IT", "HR", "Sales", "IT", "Sales", "HR", "IT", "Sales", "Sales"],
    "salary": [50000.0, 70000.0, 48000.0, 85000.0, 68000.0, 95000.0, 45000.0, 62000.0, 72000.0, 90000.0],
    "promoted": ["no", "yes", "no", "yes", "no", "yes", "no", "no", "yes", "yes"]
}
df = pd.DataFrame(data)

# 2. Define the configuration for the classification task
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
    "stratify": False
}

# 3. Execute the pipeline
results = run_ml_pipeline(df, config)

# 4. View results
print(f"Task type: {results['task']}")
print(f"Model used: {results['config']['algorithm']}")
print(f"Evaluation Metrics: {results['evaluation_metrics']}")
print(f"Test Set Predictions: {results['predictions']}")
```

---

## Running the Tests

To run all unit and integration tests inside the repository, execute:

```powershell
python -m pytest
```
