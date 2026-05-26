# AutoAnalyst AI - 8-Week Execution Plan

## Overview

This plan organizes AutoAnalyst AI across 8 weeks for 14 members divided into 7 sub-teams. Each week includes technical work, documentation work, GitHub expectations, and an end-of-week review checklist.

Detailed weekly task files are available in [`docs/weekly_tasks/`](weekly_tasks/). Each detailed file includes sub-team tasks, deliverables, suggested commit messages, and end-of-week checklists.

Integration strategy: every week should move the project closer to one end-to-end workflow powered by `src/autoanalyst/pipeline.py`. Teams should document how their outputs connect to the central pipeline and dashboard.

## Week 1: Project Setup & Team Onboarding

### Main Objective

Prepare the repository, team roles, branches, GitHub workflow, dataset selection, and initial documentation.

### Sub-Team Tasks

| Team | Tasks |
|---|---|
| Team 1: Project Management & GitHub | Prepare GitHub repo, project board, issues, branches, PR rules, and team workflow. |
| Team 2: Data Understanding & Profiling | Help choose a suitable dataset and prepare initial data dictionary. |
| Team 3: EDA & Visualization | Review dataset columns and suggest possible EDA charts. |
| Team 4: Preprocessing & Feature Engineering | Identify expected data cleaning and preprocessing challenges. |
| Team 5: Machine Learning | Identify the ML problem type: classification, regression, or both. |
| Team 6: Evaluation & Insights | Define suitable evaluation metrics. |
| Team 7: Reporting & Dashboard | Prepare initial README and report structure. |

### Expected Technical Deliverables

- Repository can be installed and tested locally.
- Dataset candidate selected.
- Initial technical scope confirmed.
- End-to-end workflow and pipeline contracts reviewed by all teams.

### Expected Documentation Deliverables

- Team roles documented.
- Dataset selection notes.
- Initial README update.
- Weekly update file completed for Week 1.

### GitHub Deliverables

- Branches created.
- Issues created for team tasks.
- PR rules explained.
- Project board prepared if used.

### End-of-Week Review Checklist

- [ ] Every member has repository access.
- [ ] Every team knows its branch.
- [ ] Dataset is selected or shortlisted.
- [ ] Baseline tests run successfully.
- [ ] Week 1 update is completed.

## Week 2: Data Understanding & Basic Profiling

### Main Objective

Understand the dataset and create the basic data profiling module.

### Sub-Team Tasks

| Team | Tasks |
|---|---|
| Team 1 | Monitor issues, branches, and PRs. |
| Team 2 | Build data profiling module: shape, columns, data types, missing values, duplicates, unique values, basic statistics. |
| Team 3 | Create simple initial charts for numeric and categorical columns. |
| Team 4 | Document preprocessing problems found in the data. |
| Team 5 | Validate target column and ML task feasibility. |
| Team 6 | Write initial observations from the dataset. |
| Team 7 | Update README with dataset overview. |

### Expected Technical Deliverables

- Data profiling module.
- Missing values report.
- Duplicate count.
- Data types summary.
- Unique values summary.
- Profiling outputs compatible with `PipelineResult.profile` and `PipelineResult.missing_values_report`.

### Expected Documentation Deliverables

- Dataset overview report.
- README dataset section updated.
- Week 2 update completed.

### GitHub Deliverables

- Pull Requests opened for profiling and documentation updates.
- Issues updated with progress.

### End-of-Week Review Checklist

- [ ] Profiling functions are tested.
- [ ] Dataset profile is understandable.
- [ ] README includes dataset overview.
- [ ] Week 2 update is completed.

## Week 3: Exploratory Data Analysis

### Main Objective

Perform deeper exploratory data analysis and extract initial insights.

### Sub-Team Tasks

| Team | Tasks |
|---|---|
| Team 1 | Review Week 2 PRs and merge clean work into `develop`. |
| Team 2 | Support EDA team with column descriptions and data meaning. |
| Team 3 | Build EDA module: distributions, correlation matrix, categorical analysis, target analysis. |
| Team 4 | Identify columns needing cleaning based on EDA. |
| Team 5 | Study relationships between features and target. |
| Team 6 | Extract first set of EDA insights. |
| Team 7 | Add EDA figures and explanations to the report draft. |

### Expected Technical Deliverables

- EDA module.
- Correlation analysis.
- Target analysis.
- Visual charts saved.
- EDA outputs structured for `PipelineResult.eda_results`.

### Expected Documentation Deliverables

- Initial insights document.
- Report updated with EDA section.
- Week 3 update completed.

### GitHub Deliverables

- EDA PR opened.
- Figures or notebook outputs documented.
- Review comments resolved.

### End-of-Week Review Checklist

- [ ] EDA outputs are reproducible.
- [ ] Charts are clear and labeled.
- [ ] Initial insights are written clearly.
- [ ] Week 3 update is completed.

## Week 4: Data Cleaning & Preprocessing

### Main Objective

Prepare the dataset for machine learning.

### Sub-Team Tasks

| Team | Tasks |
|---|---|
| Team 1 | Manage conflicts and review PRs. |
| Team 2 | Update data dictionary after cleaning decisions. |
| Team 3 | Compare charts before and after cleaning if useful. |
| Team 4 | Build preprocessing pipeline: missing values, duplicates, encoding, scaling, train/test split. |
| Team 5 | Test preprocessing output with a simple baseline model. |
| Team 6 | Document impact of cleaning on data quality. |
| Team 7 | Update report with data cleaning and preprocessing section. |

### Expected Technical Deliverables

- Cleaning module.
- Preprocessing pipeline.
- Encoded data.
- Train/test split ready.
- Cleaned and model-ready data compatible with the central pipeline.

### Expected Documentation Deliverables

- Cleaning report.
- Report updated with preprocessing section.
- Week 4 update completed.

### GitHub Deliverables

- Preprocessing PR opened.
- Tests added for cleaning behavior.
- Review comments resolved.

### End-of-Week Review Checklist

- [ ] Preprocessing handles missing values and duplicates.
- [ ] Encoded data is model-ready.
- [ ] Train/test split works.
- [ ] Week 4 update is completed.

## Week 5: Feature Engineering & Baseline Models

### Main Objective

Build the first working version of the machine learning workflow.

### Sub-Team Tasks

| Team | Tasks |
|---|---|
| Team 1 | Organize a code review session. |
| Team 2 | Review final feature columns after preprocessing. |
| Team 3 | Visualize important features if available. |
| Team 4 | Build feature engineering module and create useful derived features if suitable. |
| Team 5 | Train baseline models such as Logistic Regression, Decision Tree, Random Forest, Linear Regression, or other suitable models. |
| Team 6 | Prepare model comparison table. |
| Team 7 | Update report with baseline model results. |

### Expected Technical Deliverables

- Feature engineering module.
- Baseline models trained.
- First model results.
- Metrics comparison table.
- Baseline model path callable from `run_analysis_pipeline` when a target column is configured.

### Expected Documentation Deliverables

- Model results documented.
- Feature notes documented.
- Week 5 update completed.

### GitHub Deliverables

- Modeling and feature PRs opened.
- Tests or verification notes included.
- Review session notes recorded.

### End-of-Week Review Checklist

- [ ] Baseline model runs successfully.
- [ ] Feature engineering is documented.
- [ ] Metrics comparison table exists.
- [ ] Week 5 update is completed.

## Week 6: Model Improvement & Evaluation

### Main Objective

Improve model results and create a professional evaluation module.

### Sub-Team Tasks

| Team | Tasks |
|---|---|
| Team 1 | Check code quality and consistency. |
| Team 2 | Review the effect of selected columns on results. |
| Team 3 | Create visual charts for model results. |
| Team 4 | Improve preprocessing if model issues appear. |
| Team 5 | Try additional models and simple hyperparameter tuning. |
| Team 6 | Build evaluation module: classification report, confusion matrix, accuracy, precision, recall, F1-score, MAE, RMSE, R² depending on the task. |
| Team 7 | Update report with model evaluation section. |

### Expected Technical Deliverables

- Improved model results.
- Evaluation module.
- Confusion matrix or regression metrics.
- Best model selected.
- Evaluation output structured for `PipelineResult.evaluation_results`.

### Expected Documentation Deliverables

- Evaluation report updated.
- Model comparison explanation.
- Week 6 update completed.

### GitHub Deliverables

- Evaluation PR opened.
- Model improvement PR opened if needed.
- Tests or verification notes included.

### End-of-Week Review Checklist

- [ ] Evaluation metrics match the ML problem type.
- [ ] Best model decision is justified.
- [ ] Results are reproducible.
- [ ] Week 6 update is completed.

## Week 7: Insight Generation, Report & Dashboard

### Main Objective

Connect the system outputs into a clear product-like experience.

### Sub-Team Tasks

| Team | Tasks |
|---|---|
| Team 1 | Review final feature branches and prepare integration into `develop`. |
| Team 2 | Review final dataset documentation. |
| Team 3 | Prepare final visualizations for dashboard. |
| Team 4 | Ensure the full pipeline works from raw data to processed data. |
| Team 5 | Save or document the best model. |
| Team 6 | Build a rule-based insight generator that produces readable insights and recommendations. |
| Team 7 | Build or improve Streamlit dashboard and final report draft. |

### Expected Technical Deliverables

- Insight generator.
- Streamlit dashboard.
- Best model documented.
- End-to-end pipeline connected.
- Dashboard calls `run_analysis_pipeline` instead of duplicating backend analysis logic.

### Expected Documentation Deliverables

- Final report draft.
- Dashboard usage notes.
- Week 7 update completed.

### GitHub Deliverables

- Dashboard/reporting PR opened.
- Final integration PRs reviewed.
- Issues updated with final status.

### End-of-Week Review Checklist

- [ ] Dashboard runs locally.
- [ ] Insights are readable and useful.
- [ ] Report draft is complete enough for review.
- [ ] Week 7 update is completed.

## Week 8: Final Integration, Testing & Presentation

### Main Objective

Finalize the project and prepare it for GitHub, demo, presentation, and portfolio use.

### Sub-Team Tasks

| Team | Tasks |
|---|---|
| Team 1 | Merge approved work into `develop`, prepare final release into `main`, organize GitHub issues and PRs. |
| Team 2 | Review dataset documentation. |
| Team 3 | Review chart quality and visualization consistency. |
| Team 4 | Test the preprocessing pipeline end-to-end. |
| Team 5 | Test the modeling workflow end-to-end. |
| Team 6 | Review insights and recommendations. |
| Team 7 | Prepare final README, screenshots, demo instructions, final report, and presentation support. |

### Expected Technical Deliverables

- Final dashboard.
- End-to-end pipeline validation.
- Final tested project.
- Integration tests confirm dataset upload-to-dashboard workflow outputs are available.

### Expected Documentation Deliverables

- Final README.
- Final report.
- Final presentation outline.
- Demo instructions.
- Optional LinkedIn post draft.

### GitHub Deliverables

- Final GitHub repository ready.
- Approved PRs merged.
- Issues organized or closed.
- Release notes prepared.

### End-of-Week Review Checklist

- [ ] `python -m compileall -q app src tests` passes.
- [ ] `pytest` passes.
- [ ] Dashboard demo works.
- [ ] Final report is complete.
- [ ] Presentation/demo instructions are ready.
- [ ] Week 8 update is completed.
