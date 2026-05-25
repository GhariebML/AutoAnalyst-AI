# Week 06 — Model Improvement & Evaluation

## Main Objective
Improve model performance and create a professional evaluation system.

Week 6 builds on baseline models from Week 5.

---

## Expected End-of-Week Outcome

By the end of Week 6, the project should have:

- Improved model results.
- Evaluation module.
- Classification or regression metrics.
- Confusion matrix or regression plots.
- Best model selected.
- Evaluation report updated.

---

# Team 1 — Project Management & GitHub

## Required Tasks

1. Review Week 5 PRs.
2. Merge stable modeling work into `develop`.
3. Create Week 6 Issues.
4. Check code quality and naming consistency.
5. Make sure tests still pass.

## Deliverables

- Week 5 work merged.
- Week 6 Issues created.
- Code quality notes.
- Testing status summary.

## Suggested Commit Message

```text
docs(project): update week 6 evaluation coordination
```

---

# Team 2 — Data Understanding & Profiling

## Required Tasks

1. Review the effect of features on results.
2. Document any features that seem highly important.
3. Update feature documentation if feature importance is available.
4. Add notes about data limitations.

## Deliverables

- Feature impact notes.
- Dataset limitation notes.
- Updated data documentation.

## Suggested Commit Message

```text
docs(data): add feature impact and limitation notes
```

---

# Team 3 — EDA & Visualization

## Required Tasks

1. Create evaluation visualizations:
 - Confusion matrix heatmap for classification
 - Predicted vs actual plot for regression
 - Metrics comparison chart
 - Feature importance chart if available

2. Save charts in:

```text
reports/figures/
```

## Deliverables

- Evaluation charts.
- Visual comparison of models.
- Figures ready for report/dashboard.

## Suggested Commit Message

```text
feat(visualization): add model evaluation charts
```

---

# Team 4 — Preprocessing & Feature Engineering

## Required Tasks

1. Improve preprocessing if model results show problems.
2. Adjust features if needed.
3. Make sure preprocessing pipeline is reusable.
4. Document any changes.

## Deliverables

- Improved preprocessing if needed.
- Updated feature engineering module.
- Notes explaining changes.

## Suggested Commit Message

```text
refactor(preprocessing): improve pipeline for model evaluation
```

---

# Team 5 — Machine Learning

## Required Tasks

1. Try improved models or simple tuning:
 - Random Forest tuning
 - Gradient Boosting if available
 - Class weight handling if imbalanced
 - Simple parameter changes

2. Compare improved results with baseline results.
3. Save final best model information.

## Deliverables

- Improved model results.
- Best model selected.
- Model comparison updated.

## Suggested Commit Message

```text
feat(modeling): improve and compare machine learning models
```

---

# Team 6 — Evaluation & Insights

## Required Tasks

1. Implement evaluation module:

```text
src/autoanalyst/evaluation/evaluator.py
```

2. Add functions for classification metrics:
 - Accuracy
 - Precision
 - Recall
 - F1-score
 - Confusion matrix

3. Add functions for regression metrics:
 - MAE
 - MSE
 - RMSE
 - R² Score

4. Create:

```text
reports/model_evaluation_summary.md
```

## Deliverables

- Evaluation module.
- Metrics functions.
- Evaluation summary.
- Best model explanation.

## Suggested Commit Message

```text
feat(evaluation): add model evaluation module
```

---

# Team 7 — Reporting & Dashboard

## Required Tasks

1. Add evaluation section to dashboard.
2. Add visual model comparison.
3. Add best model summary.
4. Update final report draft with evaluation results.

## Deliverables

- Dashboard evaluation section.
- Report updated.
- README updated if needed.

## Suggested Commit Message

```text
feat(dashboard): add model evaluation section
```

---

# End-of-Week Checklist

- [ ] Evaluation module works.
- [ ] Improved models tested.
- [ ] Best model selected.
- [ ] Metrics table completed.
- [ ] Evaluation visuals created.
- [ ] Report/dashboard updated.
- [ ] Pull Requests opened to `develop`.
- [ ] `docs/weekly_updates/week_06.md` updated.

---

# Week 6 Leads Into Week 7

Week 6 identifies the best model and explains its performance.
Week 7 will turn results into insights, final report, and dashboard experience.
