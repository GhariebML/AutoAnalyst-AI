# AutoAnalyst AI — Autonomous Agent Specifications

---

## 1. Agent Design Principles

Every autonomous agent in the AutoAnalyst AI system conforms to strict engineering and reliability principles:

1. **Deterministic Foundation**: Agents do not invent statistics. All numerical values, metrics, distributions, and model performance scores are computed via deterministic analytical tools from `src/autoanalyst/tools/`.
2. **Strict Grounding**: System prompts prohibit hallucination. Empirical evidence must cite exact dataset counts, column names, correlations, or evaluation metrics.
3. **Structured Outputs**: All LLM reasoning produces Pydantic validated data objects (`Fact`, `Evidence`, `Interpretation`, `Recommendation`, `Confidence`).
4. **Graceful Fault Tolerance**: If LLM generation fails or hits provider rate limits, deterministic fallback syntheses ensure 100% pipeline completion.

---

## 2. Specialized Agent Specifications

### 🔍 1. DataProfilingAgent
- **Class**: `DataProfilingAgent` (`src/autoanalyst/agents/profiling_agent.py`)
- **Primary Objective**: Audit dataset integrity, identify column data types, detect missing values, and flag duplicate entries.
- **Allowed Tools**:
  - `profile_dataset(df)`: Calculates dimensions, missing totals, duplicate counts, and health score.
  - `missingness_report(df)`: Granular column-by-column missing percentage.
- **Decision Invariant**:
  - If duplicate rows exist $\to$ flag for duplicate deduplication in preprocessing.
  - If missing values $> 0$ $\to$ flag for imputation.
  - Compute Health Score: $100 - (\text{missing\_ratio} \times 50 + \text{dup\_ratio} \times 50)$.

---

### 📈 2. EDAAgent
- **Class**: `EDAAgent` (`src/autoanalyst/agents/eda_agent.py`)
- **Primary Objective**: Statistical distribution analysis, skewness discovery, multivariate outlier identification, and bivariate correlation mapping.
- **Allowed Tools**:
  - `distribution_analysis(df)`: Computes mean, standard deviation, skewness, kurtosis, and quartiles.
  - `correlation_analysis(df, method='pearson')`: Generates pairwise correlation matrix.
  - `outlier_detection(df)`: Flags anomalies using IQR and Isolation Forests.
- **Decision Invariant**:
  - If correlation $|r| > 0.85$ between two features $\to$ flag potential multicollinearity risk.
  - If skewness $> 2.0$ $\to$ flag for log transformation.

---

### ⚙️ 3. PreprocessingAgent
- **Class**: `PreprocessingAgent` (`src/autoanalyst/agents/preprocessing_agent.py`)
- **Primary Objective**: Formulate and execute data cleaning, missingness resolution, outlier treatment, and categorical encoding.
- **Allowed Tools**:
  - `generate_preprocessing_plan(df, profile, eda)`: Proposes step-by-step cleaning operations.
  - `execute_cleaning(df, plan)`: Applies median/mode imputation, drops duplicates.
  - `encode_features(df)`: Executes One-Hot Encoding with cardinality threshold guards ($N_{\text{unique}} \le 50$).
- **Human-In-The-Loop (HITL)**:
  - When `require_approval = True`, the orchestrator pauses execution at this state and yields control to the human reviewer before applying modifications to downstream ML models.

---

### 🤖 4. MachineLearningAgent
- **Class**: `MachineLearningAgent` (`src/autoanalyst/agents/ml_agent.py`)
- **Primary Objective**: Determine optimal predictive task, train candidate model zoos using stratified k-fold cross-validation, and select the champion algorithm.
- **Allowed Tools**:
  - `infer_ml_task(df, target_column)`: Detects binary classification, multiclass, or regression.
  - `benchmark_models(df, target_column, task)`: Trains `RandomForest`, `GradientBoosting`, `Ridge`, `LogisticRegression` with cross-validation.
- **Decision Invariant**:
  - Continuous numeric targets with high uniqueness are automatically assigned to regression models even if user specifies classification.
  - The model with the highest validation metric ($R^2$ for regression, $F_1$ or ROC-AUC for classification) is crowned the Champion Model.

---

### 🩺 5. EvaluationAgent
- **Class**: `EvaluationAgent` (`src/autoanalyst/agents/evaluation_agent.py`)
- **Primary Objective**: Holdout diagnostic evaluation, confusion matrix generation, and permutation feature importance calculation.
- **Allowed Tools**:
  - `evaluate_model(model, X_test, y_test, task)`: Computes holdout accuracy, precision, recall, F1, ROC-AUC, RMSE, MAE, R².
  - `calculate_feature_importances(model, X_test, y_test)`: Calculates permutation importance scores for top features.

---

### 📑 6. ReportingAgent
- **Class**: `ReportingAgent` (`src/autoanalyst/agents/reporting_agent.py`)
- **Primary Objective**: Synthesize strategic insights, formulate executive takeaways, and compile publication-ready multi-format artifacts.
- **Allowed Tools**:
  - `compile_report(run_state, output_format)`: Generates responsive Cyber Dark Chart.js HTML, JSON, and Markdown reports.
  - `detect_drift(reference_df, current_df)`: Analyzes distribution drift between datasets.
