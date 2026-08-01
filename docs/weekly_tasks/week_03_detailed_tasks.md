# Week 03 — Exploratory Data Analysis

## Main Objective
Perform deeper Exploratory Data Analysis and extract meaningful patterns, relationships, and early insights from the dataset.

Week 3 builds directly on the profiling work completed in Week 2.

---

## Expected End-of-Week Outcome

By the end of Week 3, the project should have:

- EDA module with useful analysis functions.
- Distribution charts.
- Correlation analysis.
- Target analysis.
- Feature-target relationship charts.
- Initial insight document based on EDA.
- Report updated with EDA section.

---

# Team 1 — Project Management & GitHub

## Required Tasks

1. Review Week 2 PRs.
2. Merge approved work into `develop`.
3. Create Week 3 Issues for all teams.
4. Check if teams are updating weekly files correctly.
5. Manage conflicts between EDA, reporting, and preprocessing teams.

## Deliverables

- Week 2 PRs reviewed.
- Week 3 Issues created.
- Project board updated.
- Integration notes written if needed.

## Suggested Commit Message

```text
docs(project): update week 3 tracking and integration notes
```

---

# Team 2 — Data Understanding & Profiling

## Required Tasks

1. Support Team 3 with column meaning and data dictionary.
2. Improve `docs/data_dictionary.md` based on actual analysis.
3. Add column grouping:
 - Numerical features
 - Categorical features
 - Target column
 - Dropped/ignored columns if any

4. Validate if any columns need special interpretation.

## Deliverables

- Updated data dictionary.
- Column grouping documented.
- Notes to support EDA interpretation.

## Suggested Commit Message

```text
docs(data): update data dictionary for EDA interpretation
```

---

# Team 3 — EDA & Visualization

## Required Tasks

1. Build or improve EDA module:

```text
src/autoanalyst/eda/analyzer.py
```

2. Add functions for:
 - Numeric distributions
 - Categorical distributions
 - Correlation matrix
 - Target distribution
 - Feature vs target analysis

3. Generate and save charts in:

```text
reports/figures/
```

4. Create:

```text
reports/eda_summary.md
```

## Deliverables

- EDA module improved.
- Correlation matrix created.
- Distribution charts saved.
- Target analysis completed.
- EDA summary written.

## Suggested Commit Message

```text
feat(eda): add correlation and target analysis
```

---

# Team 4 — Preprocessing & Feature Engineering

## Required Tasks

1. Use EDA results to identify:
 - Outliers
 - Skewed numerical columns
 - High-cardinality categorical columns
 - Columns that should be dropped
 - Columns that need transformation

2. Update:

```text
docs/preprocessing_plan.md
```

3. Add notes about cleaning decisions.

## Deliverables

- Updated preprocessing plan based on EDA.
- List of outlier columns.
- List of transformation needs.

## Suggested Commit Message

```text
docs(preprocessing): update cleaning decisions from EDA
```

---

# Team 5 — Machine Learning

## Required Tasks

1. Study relationship between features and target.
2. Identify promising features.
3. Identify possible weak/noisy features.
4. Update:

```text
docs/modeling_plan.md
```

5. Prepare for baseline modeling in Week 5.

## Deliverables

- Feature-target relationship notes.
- Modeling plan updated.
- Initial feature selection suggestions.

## Suggested Commit Message

```text
docs(modeling): add feature-target analysis notes
```

---

# Team 6 — Evaluation & Insights

## Required Tasks

1. Review EDA outputs from Team 3.
2. Write insights in simple professional language:
 - What patterns exist?
 - What variables seem important?
 - What data quality issues matter?
 - What business or practical meaning can be extracted?

3. Update:

```text
reports/initial_insights.md
```

4. Start structure for rule-based insights:

```text
src/autoanalyst/insights/insight_generator.py
```

## Deliverables

- EDA insights documented.
- Initial insight generator skeleton.
- Recommendations draft.

## Suggested Commit Message

```text
docs(insights): add EDA-based insights and recommendations
```

---

# Team 7 — Reporting & Dashboard

## Required Tasks

1. Add EDA section to report draft.
2. Add EDA charts to dashboard.
3. Improve Streamlit sidebar/navigation if needed.
4. Add chart display section:
 - Distribution charts
 - Correlation matrix
 - Target chart

## Deliverables

- Dashboard displays EDA charts.
- Report includes EDA section.
- README mentions EDA capabilities.

## Suggested Commit Message

```text
feat(dashboard): add EDA visualization section
```

---

# End-of-Week Checklist

- [ ] EDA module works.
- [ ] Charts saved in `reports/figures/`.
- [ ] EDA summary created.
- [ ] Insights updated.
- [ ] Preprocessing plan updated from EDA findings.
- [ ] Dashboard includes EDA view.
- [ ] Pull Requests opened to `develop`.
- [ ] `docs/weekly_updates/week_03.md` updated.

---

# Week 3 Leads Into Week 4

Week 3 identifies real data problems and relationships.
Week 4 will use these findings to clean and preprocess the data properly.
