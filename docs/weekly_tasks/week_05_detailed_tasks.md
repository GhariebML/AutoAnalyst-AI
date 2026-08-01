# Week 05 — Feature Engineering & Baseline Models

## Main Objective
Build the first complete machine learning workflow using cleaned and prepared data.

Week 5 depends on the preprocessing pipeline from Week 4.

---

## Expected End-of-Week Outcome

By the end of Week 5, the project should have:

- Feature engineering module.
- Baseline models trained.
- Initial model comparison.
- First model metrics table.
- Baseline results documented.

---

# Team 1 — Project Management & GitHub

## Required Tasks

1. Review Week 4 PRs.
2. Merge stable preprocessing work into `develop`.
3. Create Week 5 Issues.
4. Organize a code review session.
5. Ensure Team 4 and Team 5 work is aligned.

## Deliverables

- Week 4 merged.
- Week 5 Issues created.
- Code review notes.
- Integration plan for modeling.

## Suggested Commit Message

```text
docs(project): update week 5 modeling coordination
```

---

# Team 2 — Data Understanding & Profiling

## Required Tasks

1. Review final columns used for modeling.
2. Confirm that the selected features make sense.
3. Update:

```text
docs/data_dictionary.md
docs/data_cleaning_decisions.md
```

4. Add notes for any engineered features.

## Deliverables

- Final feature list updated.
- Engineered feature descriptions.
- Modeling data documentation.

## Suggested Commit Message

```text
docs(data): update final modeling feature descriptions
```

---

# Team 3 — EDA & Visualization

## Required Tasks

1. Visualize important features if available.
2. Create charts that help explain model input.
3. Prepare charts for model results:
 - Feature importance placeholder
 - Metrics comparison chart placeholder

## Deliverables

- Feature visualizations.
- Model result chart templates.
- Figures saved.

## Suggested Commit Message

```text
feat(eda): add feature analysis visuals for modeling
```

---

# Team 4 — Preprocessing & Feature Engineering

## Required Tasks

1. Implement feature engineering module:

```text
src/autoanalyst/feature_engineering/feature_builder.py
```

2. Add functions for:
 - Selecting features
 - Creating simple derived features if useful
 - Separating features and target
 - Returning model-ready datasets

3. Make sure it integrates with preprocessing.

## Deliverables

- Feature engineering module.
- Feature-target split.
- Model-ready data function.
- Documentation comments.

## Suggested Commit Message

```text
feat(features): add feature engineering workflow
```

---

# Team 5 — Machine Learning

## Required Tasks

1. Implement baseline models in:

```text
src/autoanalyst/modeling/classification.py
src/autoanalyst/modeling/regression.py
```

2. Train suitable baseline models:
 - Logistic Regression or Linear Regression
 - Decision Tree
 - Random Forest

3. Save model results in a structured format.

4. Create:

```text
reports/model_baseline_results.md
```

## Deliverables

- Baseline models trained.
- Model results table.
- Best baseline model identified.
- Modeling report draft.

## Suggested Commit Message

```text
feat(modeling): train baseline machine learning models
```

---

# Team 6 — Evaluation & Insights

## Required Tasks

1. Prepare metrics comparison table.
2. Evaluate baseline model results.
3. Add explanation:
 - Which model performed best?
 - Why might it be better?
 - What are possible limitations?

4. Update:

```text
reports/initial_insights.md
```

## Deliverables

- Baseline evaluation table.
- Initial model insights.
- Limitations documented.

## Suggested Commit Message

```text
docs(evaluation): add baseline model comparison insights
```

---

# Team 7 — Reporting & Dashboard

## Required Tasks

1. Add modeling section to report.
2. Add model result display to dashboard:
 - Metrics table
 - Best model name
 - Short model explanation

3. Update README with modeling capabilities.

## Deliverables

- Report updated with baseline models.
- Dashboard model section.
- README updated.

## Suggested Commit Message

```text
feat(dashboard): add baseline model results section
```

---

# End-of-Week Checklist

- [ ] Feature engineering module works.
- [ ] Baseline models trained.
- [ ] Model results saved.
- [ ] Evaluation table created.
- [ ] Report updated.
- [ ] Dashboard shows model results.
- [ ] Pull Requests opened to `develop`.
- [ ] `docs/weekly_updates/week_05.md` updated.

---

# Week 5 Leads Into Week 6

Week 5 creates baseline model results.
Week 6 will improve and evaluate the models more professionally.
