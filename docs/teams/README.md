# Team Documentation Hub

This folder contains professional work guides for each AutoAnalyst AI sub-team.

Each team document explains:

- Team mission
- Assigned members
- Branch name
- Main folders
- Core responsibilities
- End-to-end pipeline integration duty
- Weekly focus
- Expected deliverables
- Definition of Done
- Pull Request checklist

## Team Documents

| Team | Responsibility | Document |
|---|---|---|
| Team 1 | Project Management & GitHub | [`team_01_project_management_github.md`](team_01_project_management_github.md) |
| Team 2 | Data Understanding & Profiling | [`team_02_data_understanding_profiling.md`](team_02_data_understanding_profiling.md) |
| Team 3 | EDA & Visualization | [`team_03_eda_visualization.md`](team_03_eda_visualization.md) |
| Team 4 | Preprocessing & Feature Engineering | [`team_04_preprocessing_feature_engineering.md`](team_04_preprocessing_feature_engineering.md) |
| Team 5 | Machine Learning | [`team_05_machine_learning.md`](team_05_machine_learning.md) |
| Team 6 | Evaluation & Insights | [`team_06_evaluation_insights.md`](team_06_evaluation_insights.md) |
| Team 7 | Reporting & Dashboard | [`team_07_reporting_dashboard.md`](team_07_reporting_dashboard.md) |

## Required Team Workflow

1. Pull latest `develop`.
2. Work on the assigned feature branch.
3. Keep changes focused and integration-friendly.
4. Run local validation.
5. Update weekly progress notes.
6. Open Pull Request into `develop`.
7. Request review before merge.

## Shared Integration Rule

All technical work must support the central pipeline:

```text
src/autoanalyst/pipeline.py
```

The dashboard, reports, and future agents should consume pipeline outputs instead of duplicating business logic.
