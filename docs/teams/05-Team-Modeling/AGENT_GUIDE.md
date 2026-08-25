# Team 5 — Machine Learning Agent: Developer Guide

**Team Members:** Mohamed Khaled El-Shayep (Team Leader) · Mahmoud Maher
**Branch:** `feature/modeling`
**Phase:** Multi-Agent System (Phase 2)

---

## Overview

Team 5 is responsible for the **Modeling Agent** — the autonomous machine-learning
node in the AutoAnalyst AI multi-agent pipeline.  The agent receives a cleaned
DataFrame from the Preprocessing Agent (Team 4), makes its own decisions about
task type and algorithm selection, trains and compares models, then passes
predictions and metadata to the Evaluation Agent (Team 6).

```
Preprocessing Agent ──► [Modeling Agent] ──► Evaluation Agent
       (Team 4)              (Team 5)              (Team 6)
```

---

## Repository Layout

```
src/autoanalyst/
├── agents/
│   ├── __init__.py           # Package docstring
│   ├── state.py              # Shared AutoAnalystState TypedDict
│   ├── model_decider.py      # Autonomous task/algorithm selection engine
│   ├── modeling_tools.py     # Deterministic tool wrappers (LangChain-ready)
│   └── modeling_agent.py     # LangGraph node function: modeling_node()
│
├── modeling/
│   ├── __init__.py           # Exports all model classes
│   ├── classification.py     # ClassificationModel (enhanced)
│   ├── regression.py         # RegressionModel (enhanced)
│   ├── clustering.py         # ClusteringModel (NEW)
│   └── comparator.py         # compare_*_models() helpers (NEW)
│
tests/
├── test_model_decider.py     # 14 unit tests for decision logic
├── test_modeling_tools.py    # 12 unit tests for tool wrappers
└── test_modeling_agent.py    # 12 integration tests for the agent node
```

---

## Component Reference

### 1. `AutoAnalystState` (`state.py`)

Shared TypedDict passed between every agent node.  Team 5 **reads** the
following fields:

| Field | Type | Source |
|---|---|---|
| `cleaned_df` | `pd.DataFrame` | Preprocessing Agent (Team 4) |
| `target_column` | `str \| None` | Set by user / Orchestrator |
| `profile` | `dict` | Profiling Agent (Team 2) — optional |

Team 5 **writes** the following field:

| Field | Schema |
|---|---|
| `model_results` | See *model_results schema* below |
| `errors` | Appended on failure |
| `warnings` | Appended on non-fatal issues |

#### `model_results` schema

```python
{
    "task_type":        "classification" | "regression" | "clustering",
    "algorithm_used":   str,
    "hyperparameters":  dict,
    "decision_log":     list[str],   # why this algorithm was chosen
    "train_rows":       int,
    "test_rows":        int,
    "accuracy":         float,       # classification only
    "f1_weighted":      float,       # classification only
    "rmse":             float,       # regression only
    "r2":               float,       # regression only
    "n_clusters":       int,         # clustering only
    "silhouette_score": float | None,# clustering only
    "predictions":      list,        # y_pred on test split
    "y_test":           list,        # y_true for test split
    "cluster_assignments": list,     # clustering only
    "top_features":     list[dict],  # [{feature, importance}, …]
    "comparison":       list[dict],  # multi-model ranking table
    "model_file":       str | None,  # path to .joblib serialised estimator
}
```

---

### 2. `ModelDecider` (`model_decider.py`)

Autonomous, rule-based decision engine.  No LLM API key required.

```python
from autoanalyst.agents.model_decider import ModelDecider

decider = ModelDecider(df=cleaned_df, target_column="promoted")
decision = decider.decide()

print(decision.task_type)           # "classification"
print(decision.primary_algorithm)   # "random_forest"
print(decision.hyperparameters)     # {"n_estimators": 100, "random_state": 42}
print(decision.stratify)            # True / False
print(decision.decision_log)        # step-by-step reasoning
```

#### Decision rules

| Condition | Decision |
|---|---|
| No target column | **Clustering** |
| Target is categorical / object | **Classification** |
| Target is numeric, ≤15 unique values | **Classification** |
| Target is numeric, >15 unique values | **Regression** |
| Rows < 300 + classification | **logistic_regression** |
| Rows ≥ 300 + classification | **random_forest** |
| Rows < 300 + regression | **linear_regression** |
| Rows ≥ 300 + regression | **random_forest** |
| Class imbalance < 15 % | `class_weight="balanced"` applied |

---

### 3. Tool Layer (`modeling_tools.py`)

Five deterministic tool functions wrap the model wrappers.

```python
from autoanalyst.agents.modeling_tools import (
    train_classification_tool,
    train_regression_tool,
    train_clustering_tool,
    compare_models_tool,
    get_feature_importances_tool,
    save_model_tool,
)
```

All tools return JSON-serialisable dicts (except `_model_object` which is
a private key stripped before state export).

---

### 4. `modeling_node` (`modeling_agent.py`)

The LangGraph node function.  Call it directly or register it in a LangGraph graph:

```python
from autoanalyst.agents.modeling_agent import modeling_node
from autoanalyst.agents.state import AutoAnalystState

# Direct call (deterministic mode — no LLM needed)
state: AutoAnalystState = {
    "cleaned_df": my_encoded_df,
    "target_column": "promoted",
    "errors": [],
    "warnings": [],
}
updated_state = modeling_node(state)

print(updated_state["model_results"]["task_type"])    # "classification"
print(updated_state["model_results"]["accuracy"])     # e.g. 0.875
print(updated_state["model_results"]["decision_log"]) # reasoning steps
```

#### LangGraph registration (Team 1 / Orchestrator)

```python
from langgraph.graph import StateGraph
from autoanalyst.agents.modeling_agent import modeling_node
from autoanalyst.agents.state import AutoAnalystState

graph = StateGraph(AutoAnalystState)
graph.add_node("modeling", modeling_node)
# … add edges from preprocessing_node → modeling_node → evaluation_node
```

---

## Running Tests

```powershell
# All Team 5 tests
python -m pytest tests/test_model_decider.py tests/test_modeling_tools.py tests/test_modeling_agent.py -v

# Full project suite
python -m pytest
```

---

## Integration Contract

| Contract | Detail |
|---|---|
| **Input from Team 4** | `cleaned_df` must be fully numeric (encoded) with no NaN values |
| **Output to Team 6** | `model_results["predictions"]` + `model_results["y_test"]` contain the test-split data for metric calculation |
| **Error handling** | All exceptions are caught and appended to `state["errors"]`; the node never raises |
| **JSON-safety** | `model_results` is guaranteed JSON-serialisable (no NumPy types or model objects) |
| **Model persistence** | Serialised estimator saved to `models/<algo>_estimator.joblib`; path stored in `model_results["model_file"]` |
