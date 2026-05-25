# Team 4 — Preprocessing & Feature Engineering

## Members

- Member 7
- Member 8

> Replace placeholders with real names and GitHub usernames.

## Main Mission

Team 4 owns data cleaning, preprocessing, encoding, scaling, feature engineering, and model-ready dataset preparation.

## Assigned Branch

```text
feature/preprocessing-features
```

## Main Folders

```text
src/autoanalyst/preprocessing/
src/autoanalyst/feature_engineering/
docs/
tests/
```

## Core Responsibilities

- Remove duplicates.
- Handle missing values.
- Encode categorical columns.
- Scale or transform numeric columns when needed.
- Create derived features.
- Separate features and target when needed.
- Keep preprocessing reusable and safe.

## End-to-End Integration Duty

Team 4 produces the data used by modeling and evaluation:

```text
PipelineResult.cleaned_df
PipelineResult.model_ready_df
```

Preprocessing functions must not mutate the original DataFrame unexpectedly.

## Weekly Focus

| Week | Focus |
|---|---|
| 1 | Initial preprocessing strategy |
| 2 | Preprocessing plan based on profiling |
| 3 | Cleaning decisions from EDA |
| 4 | Main preprocessing pipeline |
| 5 | Feature engineering workflow |
| 6 | Improve preprocessing based on model results |
| 7 | Stabilize full preprocessing flow |
| 8 | Final preprocessing validation |

## Expected Deliverables

- Preprocessing plan.
- Cleaning functions.
- Encoding helpers.
- Feature engineering functions.
- Model-ready data workflow.
- Tests for cleaning and features.

## Definition of Done

- Original data is preserved unless explicitly documented.
- Missing values and duplicates are handled safely.
- Outputs are compatible with modeling.
- Functions are covered by tests or verification notes.
- Pipeline integration is documented.

## Suggested Commit Messages

```text
feat(preprocessing): add reusable cleaning pipeline
feat(features): add feature-target split helper
test(preprocessing): cover missing value strategies
```
