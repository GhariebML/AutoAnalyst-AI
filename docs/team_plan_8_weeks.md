# AutoAnalyst AI - 8-Week Team Plan

## Project Overview

AutoAnalyst AI is an automated AI-powered data analyst system. The project is designed to help users move from raw datasets to useful analytical outputs through data loading, understanding, profiling, exploratory data analysis, preprocessing, feature engineering, machine learning, evaluation, insight generation, report generation, and a dashboard interface.

This project is also a training environment for professional teamwork: GitHub workflow, branches, Pull Requests, documentation, code review, testing, and clean delivery.

## Purpose of the Team Structure

The team has 14 members. To keep the project organized and manageable, the work is divided into 7 sub-teams. Each sub-team has 2 members and owns one clear responsibility area. This makes collaboration easier, reduces conflicts, and helps every member build a portfolio-ready contribution.

## 14-Member Team Organization

> Replace placeholder member names and add GitHub usernames after the team is finalized.

| Sub-Team | Members | Main Responsibility | Branch Name | Main Folder / Files |
|---|---|---|---|---|
| Team 1: Project Management & GitHub | Member 1 + Member 2 | Project management, GitHub workflow, issues, PRs, repo organization | `feature/project-management` | `docs/`, `.github/` |
| Team 2: Data Understanding & Profiling | Member 3 + Member 4 | Dataset understanding, data dictionary, profiling, missing values, duplicates | `feature/data-profiling` | `src/autoanalyst/data_profiling/`, `data/`, `docs/` |
| Team 3: EDA & Visualization | Member 5 + Member 6 | EDA, visualizations, correlations, distributions, target analysis | `feature/eda-visualization` | `src/autoanalyst/eda/`, `notebooks/`, `reports/figures/` |
| Team 4: Preprocessing & Feature Engineering | Member 7 + Member 8 | Data cleaning, preprocessing, encoding, scaling, feature engineering | `feature/preprocessing-features` | `src/autoanalyst/preprocessing/`, `src/autoanalyst/feature_engineering/` |
| Team 5: Machine Learning | Member 9 + Member 10 | Classification and regression modeling, baseline models, model improvement | `feature/modeling` | `src/autoanalyst/modeling/`, `notebooks/` |
| Team 6: Evaluation & Insights | Member 11 + Member 12 | Model evaluation, metrics, insight generation, recommendations | `feature/evaluation-insights` | `src/autoanalyst/evaluation/`, `src/autoanalyst/insights/` |
| Team 7: Reporting & Dashboard | Member 13 + Member 14 | Report generation, Streamlit dashboard, screenshots, final presentation support | `feature/reporting-dashboard` | `src/autoanalyst/reporting/`, `app/`, `reports/` |

## Expected Deliverables by Sub-Team

| Sub-Team | Expected Deliverables |
|---|---|
| Team 1 | GitHub issues, branch workflow, PR review process, docs organization, weekly tracking, final release checklist |
| Team 2 | Data dictionary, profiling module, missing values report, duplicate report, data quality summary, tests |
| Team 3 | EDA module, distribution charts, correlation analysis, categorical analysis, target analysis, visual outputs |
| Team 4 | Cleaning module, preprocessing pipeline, encoding/scaling helpers, feature engineering module, tests |
| Team 5 | Baseline classification/regression models, model comparison, improved models, modeling notes, tests |
| Team 6 | Evaluation metrics, confusion matrix/regression metrics, insight generator, recommendations, tests |
| Team 7 | Streamlit dashboard, report generation, screenshots, final report, demo instructions, presentation support |

## Team Communication Rules

- Use clear, respectful communication.
- Each sub-team should post weekly progress using the template in `docs/weekly_updates/`.
- Mention blockers early instead of waiting until the end of the week.
- Every Pull Request should include a clear summary, testing notes, and reviewer notes.
- Ask for review before merging.
- Do not push directly to `main`.
- Keep secrets, API keys, private datasets, and local paths out of the repository.

## Weekly Submission Rules

At the end of each week, every sub-team should submit:

1. Code or documentation updates on the assigned branch.
2. A Pull Request into `develop`.
3. A weekly update in `docs/weekly_updates/week_XX.md`.
4. A short list of completed work, blockers, and next-week tasks.
5. Test results or manual verification notes.

## Quality Expectations

Before opening a Pull Request, run:

```bash
python -m compileall -q app src tests
pytest
```

If a task changes the dashboard or charts, include screenshots in the Pull Request.
