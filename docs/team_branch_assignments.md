# Team Branch Assignments

This document assigns each sub-team to a professional feature branch and main work area.

## Branch Assignment Table

| Sub-Team | Members | Branch Name | Main Responsibility | Main Folder | Expected Deliverables |
|---|---|---|---|---|---|
| Team 1: Project Management & GitHub / System Integration | Mohamed Gharieb | `feature/project-management` | Project management, GitHub workflow, issues, PRs, repo organization, system integration | `docs/`, `.github/`, `src/autoanalyst/pipeline.py` | Issues, project board, PR process, docs organization, weekly tracking, integration coordination |
| Team 2: Data Understanding & Profiling | حازم + محمود ماهر | `feature/data-profiling` | Dataset understanding, data dictionary, profiling, missing values, duplicates | `src/autoanalyst/data_profiling/` | Data dictionary, profiling module, missing values report, duplicate report, tests |
| Team 3: EDA & Visualization | أيه + آيه عماد | `feature/eda-visualization` | EDA, visualizations, correlations, distributions, target analysis | `src/autoanalyst/eda/` | EDA module, charts, correlation analysis, target analysis, EDA notes |
| Team 4: Preprocessing & Feature Engineering | بسمه + رضوي | `feature/preprocessing-features` | Data cleaning, preprocessing, encoding, scaling, feature engineering | `src/autoanalyst/preprocessing/`, `src/autoanalyst/feature_engineering/` | Cleaning pipeline, preprocessing helpers, feature engineering module, tests |
| Team 5: Machine Learning | الكومي + الشايب | `feature/modeling` | Classification and regression modeling, baseline models, model improvement | `src/autoanalyst/modeling/` | Baseline models, improved models, model comparison, modeling notes, tests |
| Team 6: Evaluation & Insights | سهاد + مروة | `feature/evaluation-insights` | Model evaluation, metrics, insight generation, recommendations | `src/autoanalyst/evaluation/`, `src/autoanalyst/insights/` | Evaluation module, metrics, insight generator, recommendations, tests |
| Team 7: Reporting & Dashboard | يمني + محمد كمال | `feature/reporting-dashboard` | Report generation, Streamlit dashboard, screenshots, final presentation support | `src/autoanalyst/reporting/`, `app/`, `reports/` | Report generator, dashboard improvements, screenshots, final report, demo guide |

## Dedicated Team Documents

Professional task guides for all teams are available in:

```text
docs/teams/
```

Each guide includes mission, branch, folders, weekly focus, integration duty, deliverables, and Definition of Done.

## Branch Workflow

All team branches should be created from `develop`.

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-team-branch
```

All Pull Requests should target `develop`. The `main` branch is reserved for stable releases only.

## Required Validation Before PR

```bash
python -m compileall -q app src tests
pytest
```

## Weekly Update Requirement

Each team must update the correct weekly file:

```text
docs/weekly_updates/week_XX.md
```

Include completed tasks, changed files, PR links, blockers, decisions, and next-week plans.
