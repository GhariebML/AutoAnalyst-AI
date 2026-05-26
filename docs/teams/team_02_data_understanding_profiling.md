# Team 2 — Data Understanding & Profiling

## Members

- حازم
- محمود ماهر

## Main Mission

Team 2 owns dataset understanding, data dictionary, data loading support, data quality checks, and profiling outputs.

## Assigned Branch

```text
feature/data-profiling
```

## Main Folders

```text
src/autoanalyst/data_loading/
src/autoanalyst/data_profiling/
docs/
reports/
```

## Core Responsibilities

- Select or document the project dataset.
- Maintain `docs/data_dictionary.md` when created.
- Improve CSV/Excel loading behavior.
- Generate profile summaries: rows, columns, dtypes, missing values, duplicates, unique values.
- Document data quality limitations.
- Provide clear outputs that downstream teams can use.

## End-to-End Integration Duty

Team 2 outputs feed the central pipeline fields:

```text
PipelineResult.profile
PipelineResult.missing_values_report
PipelineResult.raw_df
```

Profiling functions should be deterministic, reusable, and safe for dashboard use.

## Weekly Focus

| Week | Focus |
|---|---|
| 1 | Dataset shortlist and initial data dictionary |
| 2 | Core profiling functions and reports |
| 3 | Column meaning and EDA support |
| 4 | Cleaning decision documentation |
| 5 | Final feature list documentation |
| 6 | Feature impact and data limitation notes |
| 7 | Final dataset documentation review |
| 8 | Final data dictionary and profile summary |

## Step-by-Step Execution Guide

Team 2 uses the shared step-by-step execution guide for dataset selection, data dictionary work, loading validation, profiling outputs, tests, and handoff notes.

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

- Dataset overview.
- Data dictionary.
- Profiling functions.
- Missing values report.
- Duplicate report.
- Data quality notes.
- Tests for loading/profiling behavior.

## Definition of Done

- Functions return structured outputs.
- Empty/bad dataset cases are handled clearly.
- Outputs can be consumed by `src/autoanalyst/pipeline.py`.
- Documentation explains columns and known limitations.
- Tests or manual verification notes are included.

## Suggested Commit Messages

```text
feat(profiling): add dataset quality summary
docs(data): update data dictionary
test(profiling): cover missing value report
```
