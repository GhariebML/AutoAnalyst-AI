# Team 3 — EDA & Visualization

## Members

- Member 5
- Member 6

> Replace placeholders with real names and GitHub usernames.

## Main Mission

Team 3 owns exploratory data analysis, statistical summaries, visualizations, correlations, distributions, and target analysis.

## Assigned Branch

```text
feature/eda-visualization
```

## Main Folders

```text
src/autoanalyst/eda/
notebooks/
reports/figures/
reports/
```

## Core Responsibilities

- Build reusable EDA functions.
- Create numeric and categorical summaries.
- Generate correlation analysis.
- Create distribution and target analysis charts.
- Save useful figures to `reports/figures/`.
- Provide clear visual outputs for dashboard and report teams.

## End-to-End Integration Duty

Team 3 outputs should be compatible with:

```text
PipelineResult.eda_results
```

EDA functions should return DataFrames, dictionaries, or figure paths that the dashboard/report can display.

## Weekly Focus

| Week | Focus |
|---|---|
| 1 | EDA questions and chart plan |
| 2 | Initial charts and basic summaries |
| 3 | Full EDA module and target analysis |
| 4 | Before/after cleaning visuals |
| 5 | Feature analysis visuals |
| 6 | Model evaluation charts |
| 7 | Final dashboard/report charts |
| 8 | Final visualization polish |

## Expected Deliverables

- EDA plan.
- Numeric summaries.
- Categorical summaries.
- Correlation matrix.
- Target analysis.
- Chart files and descriptions.
- EDA report notes.

## Definition of Done

- Charts have clear titles and labels.
- EDA outputs are reproducible.
- Functions do not depend on hardcoded local paths.
- Output can be called by the pipeline or documented for future integration.
- Important findings are explained in plain language.

## Suggested Commit Messages

```text
feat(eda): add categorical summary
feat(visualization): add correlation heatmap
docs(eda): explain target analysis findings
```
