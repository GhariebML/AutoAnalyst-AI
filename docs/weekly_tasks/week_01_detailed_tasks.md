# Week 01 — Project Setup & Team Onboarding

## Main Objective
Prepare the team, repository, workflow, dataset direction, and project documentation so all 7 sub-teams can start working professionally.

This week is about **organization, alignment, and preparation**. No heavy coding is required yet.

---

## Expected End-of-Week Outcome
By the end of Week 1, the project should have:

- Clear team structure.
- GitHub repository ready.
- `main`, `develop`, and feature branches prepared.
- Dataset selected or shortlisted.
- Team responsibilities documented.
- Initial README and project documentation updated.
- GitHub Issues created for Week 1 and Week 2.
- Every team understands its branch, responsibilities, and weekly workflow.

---

# Team 1 — Project Management & GitHub

## Main Responsibility
Prepare the GitHub collaboration environment and make sure all teams know how to contribute.

## Required Tasks

1. Verify that the repository is connected to GitHub:
 - Repository URL: `https://github.com/GhariebML/AutoAnalyst-AI`
 - Confirm `main` branch exists.
 - Confirm `develop` branch exists.

2. Confirm or create the feature branches:
 - `feature/project-management`
 - `feature/data-profiling`
 - `feature/eda-visualization`
 - `feature/preprocessing-features`
 - `feature/modeling`
 - `feature/evaluation-insights`
 - `feature/reporting-dashboard`

3. Review and improve documentation:
 - `README.md`
 - `CONTRIBUTING.md`
 - `docs/team_plan_8_weeks.md`
 - `docs/team_branch_assignments.md`
 - `docs/repository_settings_guide.md`

4. Create GitHub Issues for Week 1 tasks.

5. Prepare a simple GitHub workflow guide for the team:
 - Clone repo
 - Switch branch
 - Pull latest changes
 - Commit
 - Push
 - Open Pull Request

## Deliverables

- Updated GitHub workflow documentation.
- Verified branches.
- Week 1 GitHub Issues created.
- Team branch assignment confirmed.
- Pull Request rules documented.

## Suggested Commit Message

```text
docs(github): prepare week 1 collaboration workflow
```

---

# Team 2 — Data Understanding & Profiling

## Main Responsibility
Select or shortlist the dataset and start understanding its structure.

## Required Tasks

1. Search for 2 or 3 possible datasets suitable for the project.

2. Recommend one main dataset based on:
 - Clear columns
 - Suitable size
 - Has a target column
 - Good for EDA
 - Good for Machine Learning
 - Easy for beginners to understand

3. Create an initial dataset summary including:
 - Dataset name
 - Source
 - Number of rows
 - Number of columns
 - Target column
 - Problem type: classification or regression
 - Short description of each important column

4. Create an initial `data_dictionary.md`.

Recommended file:

```text
docs/data_dictionary.md
```

## Deliverables

- Dataset selected or shortlisted.
- Initial data dictionary.
- Dataset overview added to docs.
- Recommendation for the final dataset.

## Suggested Commit Message

```text
docs(data): add initial dataset overview and data dictionary
```

---

# Team 3 — EDA & Visualization

## Main Responsibility
Plan the exploratory data analysis work that will be implemented in Week 2 and Week 3.

## Required Tasks

1. Review the selected or shortlisted dataset.

2. Identify possible EDA questions:
 - What are the main numerical columns?
 - What are the main categorical columns?
 - What columns may affect the target?
 - What relationships should be visualized?

3. Suggest charts to build later:
 - Histograms
 - Bar charts
 - Box plots
 - Correlation heatmap
 - Target distribution
 - Feature vs target visualizations

4. Create an EDA planning file:

```text
docs/eda_plan.md
```

## Deliverables

- EDA questions list.
- Suggested charts list.
- Initial EDA plan.

## Suggested Commit Message

```text
docs(eda): add initial exploratory analysis plan
```

---

# Team 4 — Preprocessing & Feature Engineering

## Main Responsibility
Prepare a preprocessing strategy based on expected data issues.

## Required Tasks

1. Review dataset columns and identify:
 - Numerical columns
 - Categorical columns
 - Date/time columns if any
 - Columns with possible missing values
 - Columns that may need encoding
 - Columns that may need scaling

2. Create preprocessing strategy documentation:

```text
docs/preprocessing_plan.md
```

3. Define expected preprocessing steps:
 - Remove duplicates
 - Handle missing values
 - Encode categorical columns
 - Scale numerical columns
 - Split data into train/test

4. Suggest simple feature engineering ideas if possible.

## Deliverables

- Preprocessing plan.
- Feature engineering ideas.
- List of expected cleaning problems.

## Suggested Commit Message

```text
docs(preprocessing): add initial preprocessing strategy
```

---

# Team 5 — Machine Learning

## Main Responsibility
Define the machine learning direction for the project.

## Required Tasks

1. Review the selected dataset and target column.

2. Decide the ML task type:
 - Classification
 - Regression
 - Or both if the dataset supports it

3. Suggest baseline models.

For classification:
- Logistic Regression
- Decision Tree
- Random Forest

For regression:
- Linear Regression
- Decision Tree Regressor
- Random Forest Regressor

4. Create an ML plan file:

```text
docs/modeling_plan.md
```

## Deliverables

- ML problem definition.
- Target column confirmation.
- Baseline models list.
- Modeling plan.

## Suggested Commit Message

```text
docs(modeling): define initial machine learning plan
```

---

# Team 6 — Evaluation & Insights

## Main Responsibility
Define how model performance and insights will be measured and explained.

## Required Tasks

1. Based on the ML task, define evaluation metrics.

For classification:
- Accuracy
- Precision
- Recall
- F1-score
- Confusion Matrix

For regression:
- MAE
- MSE
- RMSE
- R² Score

2. Define how insights should be written:
 - Simple language
 - Business meaning
 - Data-driven observations
 - Recommendations

3. Create an evaluation and insights plan:

```text
docs/evaluation_insights_plan.md
```

## Deliverables

- Evaluation metrics plan.
- Insight generation plan.
- Recommendation writing structure.

## Suggested Commit Message

```text
docs(evaluation): add evaluation and insights plan
```

---

# Team 7 — Reporting & Dashboard

## Main Responsibility
Plan the final report and dashboard experience.

## Required Tasks

1. Design the report structure:

Recommended sections:
- Executive Summary
- Dataset Overview
- Data Profiling
- EDA Results
- Preprocessing
- Modeling
- Evaluation
- Insights
- Recommendations
- Conclusion

2. Plan Streamlit dashboard sections:
 - Upload dataset
 - Dataset preview
 - Data profiling
 - EDA charts
 - Model results
 - Insights
 - Report download

3. Create:

```text
docs/report_dashboard_plan.md
```

## Deliverables

- Report outline.
- Dashboard page structure.
- Initial user flow.

## Suggested Commit Message

```text
docs(reporting): add report and dashboard plan
```

---

# End-of-Week Checklist

Each team must complete:

- [ ] Work done on correct branch.
- [ ] Documentation file created or updated.
- [ ] Changes committed with clear message.
- [ ] Branch pushed to GitHub.
- [ ] Pull Request opened to `develop`.
- [ ] Weekly update added to `docs/weekly_updates/week_01.md`.
- [ ] Blockers reported if any.

---

# Week 1 Leads Into Week 2

Week 1 prepares the foundation.
Week 2 will start actual data profiling and basic analysis based on the dataset and plans created this week.
