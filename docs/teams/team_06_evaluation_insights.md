# Team 6 — Evaluation & Insights

## Members

- سهاد
- مروة

## Main Mission

Team 6 owns model evaluation, metrics, insight generation, recommendations, and the conversion of technical results into understandable findings.

## Assigned Branch

```text
feature/evaluation-insights
```

## Main Folders

```text
src/autoanalyst/evaluation/
src/autoanalyst/insights/
reports/
tests/
```

## Core Responsibilities

- Define evaluation metrics for classification and regression.
- Implement reusable metric functions.
- Create model evaluation summaries.
- Generate rule-based insights.
- Write clear recommendations.
- Help explain results in the final report.

## End-to-End Integration Duty

Team 6 owns outputs used by reporting and dashboard:

```text
PipelineResult.evaluation_results
PipelineResult.insights
```

Evaluation and insight outputs should be dictionaries/lists that are easy to display and export.

## Weekly Focus

| Week | Focus |
|---|---|
| 1 | Evaluation and insight plan |
| 2 | Initial observations from profiling |
| 3 | EDA-based insights |
| 4 | Data quality improvement notes |
| 5 | Baseline model comparison insights |
| 6 | Main evaluation module |
| 7 | Rule-based insight generator |
| 8 | Final insights and recommendations |

## Step-by-Step Execution Guide

Team 6 uses the shared step-by-step execution guide for metric selection, evaluation helpers, insight generation, reporting outputs, and validation.

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

- Evaluation plan.
- Classification/regression metric functions.
- Model evaluation summary.
- Rule-based insight generator.
- Final recommendations.
- Tests for evaluation functions.

## Definition of Done

- Metrics match the selected task type.
- Insight wording is clear and non-technical where possible.
- Outputs can be shown in dashboard and report.
- No unsupported claims are made.
- Tests or verification notes are included.

## Suggested Commit Messages

```text
feat(evaluation): add regression metrics
feat(insights): add rule-based recommendations
docs(insights): finalize model interpretation notes
```
