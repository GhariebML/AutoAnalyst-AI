# Week 02 — Data Understanding & Basic Profiling

## Main Objective
Start working with the selected dataset and create the first technical version of the data understanding and profiling workflow.

Week 2 depends on the dataset selection and planning completed in Week 1.

---

## Expected End-of-Week Outcome

By the end of Week 2, the project should have:

- Dataset loaded successfully.
- Basic profiling functions working.
- Missing values report.
- Duplicate report.
- Data types summary.
- Initial visual exploration.
- README updated with dataset overview.

---

# Team 1 — Project Management & GitHub

## Required Tasks

1. Review all Week 1 Pull Requests.
2. Merge approved PRs into `develop`.
3. Make sure every team is working on the correct branch.
4. Create Week 2 GitHub Issues.
5. Track blockers and help teams resolve Git conflicts.

## Deliverables

- Week 1 PRs reviewed.
- Week 2 Issues created.
- Updated project board.
- Weekly progress summary.

## Suggested Commit Message

```text
docs(project): update week 2 project tracking
```

---

# Team 2 — Data Understanding & Profiling

## Required Tasks

1. Implement or improve data loading and profiling modules.

Recommended files:

```text
src/autoanalyst/data_loading/loader.py
src/autoanalyst/data_profiling/profiler.py
```

2. Add functions such as:

```python
load_csv(file_path: str)
generate_basic_profile(df)
get_missing_values_report(df)
get_duplicate_count(df)
get_data_types_summary(df)
```

3. Generate a basic profiling output for the selected dataset.

4. Update:

```text
docs/data_dictionary.md
reports/data_profile_summary.md
```

## Deliverables

- Data loading works.
- Data profiling module created or improved.
- Missing values report.
- Duplicate count report.
- Data types summary.

## Suggested Commit Message

```text
feat(profiling): add basic dataset profiling functions
```

---

# Team 3 — EDA & Visualization

## Required Tasks

1. Create basic visual analysis for:
 - Numerical columns
 - Categorical columns
 - Target column distribution

2. Save generated charts in:

```text
reports/figures/
```

3. Start EDA module:

```text
src/autoanalyst/eda/analyzer.py
```

4. Add simple functions for:
 - Numeric summary
 - Categorical summary
 - Target distribution

## Deliverables

- Initial charts.
- Basic EDA functions.
- Chart files saved.
- Short EDA notes.

## Suggested Commit Message

```text
feat(eda): add initial data exploration charts
```

---

# Team 4 — Preprocessing & Feature Engineering

## Required Tasks

1. Analyze profiling output from Team 2.
2. Identify actual preprocessing needs:
 - Missing value strategy
 - Duplicate removal
 - Encoding needs
 - Scaling needs
 - Unnecessary columns

3. Update:

```text
docs/preprocessing_plan.md
```

4. Start initial preprocessing module if suitable:

```text
src/autoanalyst/preprocessing/cleaner.py
```

## Deliverables

- Updated preprocessing plan based on real data.
- List of columns requiring cleaning.
- Initial cleaner function skeletons if needed.

## Suggested Commit Message

```text
docs(preprocessing): update cleaning plan based on profiling
```

---

# Team 5 — Machine Learning

## Required Tasks

1. Confirm final target column.
2. Confirm model task type.
3. Check if target column has class imbalance or value distribution issues.
4. Update:

```text
docs/modeling_plan.md
```

5. Prepare baseline modeling file structure if needed:

```text
src/autoanalyst/modeling/classification.py
src/autoanalyst/modeling/regression.py
```

## Deliverables

- Target column confirmed.
- ML task confirmed.
- Baseline model plan updated.
- Modeling module structure checked.

## Suggested Commit Message

```text
docs(modeling): confirm target and baseline approach
```

---

# Team 6 — Evaluation & Insights

## Required Tasks

1. Review data profiling and early EDA outputs.
2. Write initial observations:
 - Missing data issues
 - Duplicate issues
 - Interesting distributions
 - Potential relationships

3. Create or update:

```text
reports/initial_insights.md
```

4. Update metrics plan if target type changed.

## Deliverables

- Initial insights file.
- Evaluation metrics confirmed.
- Notes on data quality.

## Suggested Commit Message

```text
docs(insights): add initial observations from profiling
```

---

# Team 7 — Reporting & Dashboard

## Required Tasks

1. Update README dataset section.
2. Start dashboard structure in:

```text
app/streamlit_app.py
```

3. Add simple Streamlit sections:
 - Project title
 - File uploader
 - Dataset preview
 - Dataset shape
 - Missing values table

4. Update report draft with profiling section.

## Deliverables

- Basic dashboard skeleton.
- README updated.
- Profiling section added to report draft.

## Suggested Commit Message

```text
feat(dashboard): add basic dataset upload and preview
```

---

# End-of-Week Checklist

- [ ] Dataset loads successfully.
- [ ] Profiling functions work.
- [ ] Missing values report created.
- [ ] Initial charts created.
- [ ] README updated.
- [ ] Dashboard skeleton started.
- [ ] Pull Requests opened to `develop`.
- [ ] `docs/weekly_updates/week_02.md` updated.

---

# Week 2 Leads Into Week 3

Week 2 creates the foundation for real EDA.
Week 3 will expand the visual analysis and extract stronger insights from the data.
