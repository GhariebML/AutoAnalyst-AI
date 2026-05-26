# Team 7 — Reporting & Dashboard

## Members

- يمني
- محمد كمال

## Main Mission

Team 7 owns the Streamlit dashboard, report generation, screenshots, final demo flow, and presentation support.

## Assigned Branch

```text
feature/reporting-dashboard
```

## Main Folders

```text
app/
src/autoanalyst/reporting/
reports/
docs/
```

## Core Responsibilities

- Improve the Streamlit dashboard.
- Display profile, EDA, preprocessing, model, evaluation, and insight outputs.
- Generate Markdown reports.
- Add screenshots and demo instructions.
- Prepare final report and presentation support materials.
- Keep the dashboard user-friendly for non-technical users.

## End-to-End Integration Duty

Team 7 must use the central pipeline:

```python
from autoanalyst.pipeline import PipelineConfig, run_analysis_pipeline
```

The dashboard should display `PipelineResult` fields. It should not reimplement profiling, cleaning, EDA, modeling, evaluation, or insight logic.

## Weekly Focus

| Week | Focus |
|---|---|
| 1 | Report and dashboard plan |
| 2 | Basic upload and preview dashboard |
| 3 | EDA dashboard section |
| 4 | Preprocessing dashboard section |
| 5 | Model results dashboard section |
| 6 | Evaluation dashboard section |
| 7 | Full report/dashboard workflow |
| 8 | Final README, dashboard, demo, presentation |

## Step-by-Step Execution Guide

Team 7 uses the shared step-by-step execution guide for Streamlit workflow, pipeline display, report generation, error handling, screenshots, and demo preparation.

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

- Dashboard interface.
- Report generator integration.
- Report draft and final report.
- Demo screenshots.
- Demo instructions.
- Presentation outline.

## Definition of Done

- Dashboard runs with `streamlit run app/streamlit_app.py`.
- Dashboard calls the pipeline instead of duplicating backend logic.
- User errors are handled clearly.
- Report output is readable and professional.
- Screenshots/demo notes are ready for final presentation.

## Suggested Commit Messages

```text
feat(dashboard): connect dashboard to central pipeline
feat(reporting): add report download workflow
docs(final): add demo instructions and screenshots
```
