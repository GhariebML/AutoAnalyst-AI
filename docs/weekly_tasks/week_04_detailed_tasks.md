# Week 04 — Data Cleaning & Preprocessing

## Main Objective
Build a reliable preprocessing pipeline that converts raw data into model-ready data.

Week 4 uses the data issues discovered in Week 2 and Week 3.

---

## Expected End-of-Week Outcome

By the end of Week 4, the project should have:

- Cleaning functions.
- Missing value handling.
- Duplicate removal.
- Encoding strategy.
- Scaling strategy.
- Train/test split.
- Processed dataset ready for modeling.
- Cleaning report.

---

# Team 1 — Project Management & GitHub

## Required Tasks

1. Review Week 3 PRs and merge approved changes.
2. Create Week 4 Issues.
3. Check compatibility between preprocessing and modeling teams.
4. Make sure no private datasets are pushed to GitHub.
5. Track any data-related blockers.

## Deliverables

- Week 3 PRs merged.
- Week 4 board updated.
- Data safety checked.
- Integration notes updated.

## Suggested Commit Message

```text
docs(project): update week 4 preprocessing tracking
```

---

# Team 2 — Data Understanding & Profiling

## Required Tasks

1. Update data dictionary after cleaning decisions.
2. Document:
 - Columns removed
 - Columns transformed
 - Missing value decisions
 - Encoding decisions

3. Create or update:

```text
docs/data_cleaning_decisions.md
```

## Deliverables

- Cleaning decisions documented.
- Data dictionary updated.
- Final feature list draft.

## Suggested Commit Message

```text
docs(data): document cleaning decisions and final columns
```

---

# Team 3 — EDA & Visualization

## Required Tasks

1. Compare before/after cleaning if possible:
 - Missing values before vs after
 - Distribution changes
 - Outlier changes

2. Generate visual proof of cleaning improvement.
3. Save charts in:

```text
reports/figures/
```

## Deliverables

- Before/after cleaning charts.
- Short visual summary.
- Updated EDA notes.

## Suggested Commit Message

```text
feat(eda): add before and after cleaning visuals
```

---

# Team 4 — Preprocessing & Feature Engineering

## Required Tasks

1. Implement preprocessing pipeline in:

```text
src/autoanalyst/preprocessing/cleaner.py
```

2. Add functions for:
 - Removing duplicates
 - Handling missing values
 - Encoding categorical features
 - Scaling numerical features
 - Splitting train/test data

3. Keep functions simple and reusable.

4. Save processed sample output if allowed, without uploading private data.

## Deliverables

- Preprocessing module.
- Cleaner functions.
- Train/test split function.
- Processed data workflow.

## Suggested Commit Message

```text
feat(preprocessing): add cleaning and preprocessing pipeline
```

---

# Team 5 — Machine Learning

## Required Tasks

1. Test cleaned data with a very simple model.
2. Confirm processed data shape.
3. Check that target and features are separated correctly.
4. Report any problems to Team 4.

## Deliverables

- Simple model test result.
- Notes on model-ready data.
- Feedback to preprocessing team.

## Suggested Commit Message

```text
test(modeling): validate preprocessed data with baseline model
```

---

# Team 6 — Evaluation & Insights

## Required Tasks

1. Document how cleaning improved data quality:
 - Missing values reduced
 - Duplicates removed
 - Features prepared for modeling

2. Update:

```text
reports/initial_insights.md
```

3. Prepare evaluation template for Week 5 models.

## Deliverables

- Data quality improvement notes.
- Evaluation template draft.
- Insight notes after cleaning.

## Suggested Commit Message

```text
docs(insights): document data quality improvements
```

---

# Team 7 — Reporting & Dashboard

## Required Tasks

1. Add preprocessing section to report.
2. Add dashboard view showing:
 - Missing values before/after
 - Dataset shape before/after
 - Cleaning steps applied

3. Update README with preprocessing capability.

## Deliverables

- Report updated with preprocessing.
- Dashboard preprocessing section.
- README updated.

## Suggested Commit Message

```text
feat(dashboard): add preprocessing summary section
```

---

# End-of-Week Checklist

- [ ] Cleaning module works.
- [ ] Missing values handled.
- [ ] Duplicates removed.
- [ ] Encoding implemented.
- [ ] Train/test split ready.
- [ ] Data dictionary updated.
- [ ] Dashboard/report updated.
- [ ] Pull Requests opened to `develop`.
- [ ] `docs/weekly_updates/week_04.md` updated.

---

# Week 4 Leads Into Week 5

Week 4 produces model-ready data.
Week 5 will use this cleaned data to train baseline machine learning models.
