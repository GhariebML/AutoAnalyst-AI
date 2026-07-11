# Team Roles

AutoAnalyst AI is organized into 7 teams. Each team owns one major project workstream, one branch, and one clear set of deliverables.

| Team | Members | Role | Responsibilities | Expected Deliverables | Branch |
|---|---|---|---|---|---|
| 1 | Mohamed Gharieb | Project Management & GitHub / System Integration | Repo organization, issues, PR workflow, documentation quality, integration coordination, final checklist | Docs hub, issues, roadmap, integration checklist, final contribution summary | `feature/project-management` |
| 2 | Ø­Ø§Ø²Ù… + Ù…Ø­Ù…ÙˆØ¯ Ù…Ø§Ù‡Ø± | Data Understanding & Profiling | Dataset understanding, CSV/Excel loading, validation, profiles, missing/duplicate reports | Data dictionary, loader improvements, profiling reports, data quality notes, tests | `feature/data-profiling` |
| 3 | Ø£ÙŠÙ‡ + Ø¢ÙŠÙ‡ Ø¹Ù…Ø§Ø¯ | EDA & Visualization | Numeric/categorical analysis, charts, correlation analysis, target analysis | EDA functions, charts, EDA findings, visualization notes | `feature/eda-visualization` |
| 4 | Ø¨Ø³Ù…Ù‡ + Ø±Ø¶ÙˆÙŠ | Preprocessing & Feature Engineering | Missing values, duplicates, encoding, scaling, datetime features, preprocessing pipeline | Cleaning functions, preprocessing helpers, feature modules, tests | `feature/preprocessing-features` |
| 5 | Ø§Ù„ÙƒÙˆÙ…ÙŠ + Ø§Ù„Ø´Ø§ÙŠØ¨ | Machine Learning | Classification, regression, baseline models, model comparison | Model wrappers, model comparison output, modeling notes, tests | `feature/modeling` |
| 6 | Ø³Ù‡Ø§Ø¯ + Ù…Ø±ÙˆØ© | Evaluation & Insights | Model evaluation, metrics, insight generation, recommendations | Evaluation module, metrics, insight generator, recommendation notes, tests | `feature/evaluation-insights` |
| 7 | ÙŠÙ…Ù†ÙŠ + Ù…Ø­Ù…Ø¯ ÙƒÙ…Ø§Ù„ | Reporting & Dashboard | Streamlit app, report export, UI polish, demo, presentation | Dashboard, generated report, screenshots, final demo script | `feature/reporting-dashboard` |

## Team Operating Model

- Each team works on its assigned branch.
- Each team opens Pull Requests into `develop`.
- Each Pull Request must explain what changed, how it was tested, and any limitations.
- Python code changes should include tests where practical.
- Documentation must be updated when behavior or usage changes.
- Every team must explain how its work connects to the central pipeline in `src/autoanalyst/pipeline.py`.
- For task completion details, follow `docs/team_step_by_step_execution_guide.md`.

## End-to-End Integration Ownership

| Team | Pipeline Integration Duty |
|---|---|
| Team 1 | Check that issues and PRs include integration notes and validation evidence; coordinate system integration across teams. |
| Team 2 | Ensure loading/profiling outputs match the pipeline input and profile contracts. |
| Team 3 | Return EDA outputs that can be stored in `PipelineResult.eda_results`. |
| Team 4 | Keep cleaning and feature functions deterministic and safe for repeated pipeline runs. |
| Team 5 | Make model training accept model-ready data, feature columns, and a target column. |
| Team 6 | Keep metrics and insights structured for `PipelineResult.evaluation_results` and `PipelineResult.insights`. |
| Team 7 | Use `run_analysis_pipeline` in the dashboard and avoid duplicating backend logic. |

See `docs/end_to_end_integration_strategy.md` for the full integration contract.

## Daily Update Format

```text
Team:
Done:
Next:
Blockers:
Needs review from:
```

## Review Ownership

- Team 1 reviews docs, workflow consistency, and integration readiness.
- Teams 2-5 review technical correctness of pipeline modules.
- Team 6 reviews evaluation quality and insight accuracy.
- Team 7 reviews dashboard usability and final presentation quality.
