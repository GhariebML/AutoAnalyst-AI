# Team 5 — Machine Learning

## Members

- الكومي
- الشايب

## Main Mission

Team 5 owns baseline modeling, classification/regression workflows, model comparison, model improvement, and best-model documentation.

## Assigned Branch

```text
feature/modeling
```

## Main Folders

```text
src/autoanalyst/modeling/
notebooks/
reports/
tests/
```

## Core Responsibilities

- Confirm machine learning task type.
- Build baseline classification and regression models.
- Compare simple models professionally.
- Improve models using safe beginner-friendly methods.
- Document assumptions, target column, and limitations.
- Provide model outputs to evaluation and dashboard teams.

## End-to-End Integration Duty

Team 5 should make modeling compatible with:

```text
PipelineConfig.target_column
PipelineConfig.model_task
PipelineResult.model_results
```

Modeling should consume model-ready data from the pipeline, not reload or clean data independently.

## Weekly Focus

| Week | Focus |
|---|---|
| 1 | ML problem definition and baseline plan |
| 2 | Target feasibility validation |
| 3 | Feature-target relationship notes |
| 4 | Test simple model on preprocessed data |
| 5 | Baseline model implementation |
| 6 | Model improvement and comparison |
| 7 | Best model documentation |
| 8 | Final modeling workflow validation |

## Step-by-Step Execution Guide

Team 5 uses the shared step-by-step execution guide for model input checks, baseline models, model comparison, validation, and handoff to evaluation.

Detailed instructions are available in:

```text
docs/team_step_by_step_execution_guide.md
```

Before opening a Pull Request, each team should confirm:

- The assigned task is complete.
- The changed files match the team responsibility.
- Outputs are documented for downstream teams.
- Tests or manual verification notes are included.
- The Pull Request targets `develop`.

## Expected Deliverables

- Modeling plan.
- Baseline models.
- Model comparison table.
- Best model summary.
- Modeling tests or verification notes.
- Documentation of limitations.

## Definition of Done

- Model code accepts prepared features and target.
- Results are reproducible using `random_state`.
- Metrics are passed to Team 6.
- Modeling does not duplicate preprocessing logic.
- Best model choice is explained clearly.

## Suggested Commit Messages

```text
feat(modeling): train baseline classification model
feat(modeling): add model comparison helper
docs(modeling): document selected best model
```
