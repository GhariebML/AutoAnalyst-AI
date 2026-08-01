# Week 07 — Insight Generation, Report & Dashboard

## Main Objective
Turn technical results into a clear product experience with insights, report generation, and dashboard integration.

Week 7 depends on the best model and evaluation results from Week 6.

---

## Expected End-of-Week Outcome

By the end of Week 7, the project should have:

- Rule-based insight generator.
- Final report draft.
- Streamlit dashboard improved.
- End-to-end pipeline connected.
- Best model documented.
- User-friendly project demo flow.

---

# Team 1 — Project Management & GitHub

## Required Tasks

1. Review Week 6 PRs.
2. Merge approved evaluation/modeling work into `develop`.
3. Create Week 7 Issues.
4. Prepare final integration checklist.
5. Identify any missing modules or broken links.

## Deliverables

- Week 6 work merged.
- Week 7 Issues created.
- Final integration checklist.
- Missing work tracker.

## Suggested Commit Message

```text
docs(project): prepare final integration checklist
```

---

# Team 2 — Data Understanding & Profiling

## Required Tasks

1. Final review of dataset documentation.
2. Make sure data dictionary is complete.
3. Confirm final dataset description is understandable.
4. Add limitations section if needed.

## Deliverables

- Final data dictionary draft.
- Dataset limitations documented.
- Data section ready for final report.

## Suggested Commit Message

```text
docs(data): finalize dataset documentation
```

---

# Team 3 — EDA & Visualization

## Required Tasks

1. Prepare final charts for dashboard and report.
2. Clean chart names and file organization.
3. Make sure figures are visually consistent.
4. Remove duplicate or low-value figures.

## Deliverables

- Final visualization set.
- Clean figures folder.
- Chart descriptions.

## Suggested Commit Message

```text
refactor(visualization): finalize report and dashboard charts
```

---

# Team 4 — Preprocessing & Feature Engineering

## Required Tasks

1. Ensure the pipeline works end-to-end:
 - Raw data input
 - Cleaning
 - Preprocessing
 - Feature engineering
 - Model-ready data

2. Add comments/docstrings if needed.
3. Check that functions are reusable.

## Deliverables

- Stable end-to-end preprocessing pipeline.
- Clean feature engineering code.
- Pipeline notes.

## Suggested Commit Message

```text
refactor(pipeline): stabilize preprocessing and feature workflow
```

---

# Team 5 — Machine Learning

## Required Tasks

1. Document the best model:
 - Model name
 - Why it was selected
 - Main metrics
 - Limitations

2. Optional: save model artifact if suitable.
3. Prepare simple model usage instructions.

## Deliverables

- Best model documentation.
- Model usage notes.
- Final modeling summary.

## Suggested Commit Message

```text
docs(modeling): document selected best model
```

---

# Team 6 — Evaluation & Insights

## Required Tasks

1. Implement or improve:

```text
src/autoanalyst/insights/insight_generator.py
```

2. Add rule-based insights such as:
 - Missing data insights
 - Strong correlation insights
 - Best model insight
 - Feature importance insights
 - Recommendation statements

3. Create:

```text
reports/final_insights.md
```

## Deliverables

- Insight generator.
- Final insights file.
- Recommendations section.

## Suggested Commit Message

```text
feat(insights): add rule-based insight generation
```

---

# Team 7 — Reporting & Dashboard

## Required Tasks

1. Build or improve report generator:

```text
src/autoanalyst/reporting/report_generator.py
```

2. Improve Streamlit dashboard:
 - Dataset upload
 - Profiling
 - EDA
 - Preprocessing summary
 - Model results
 - Insights
 - Report download if possible

3. Prepare final report draft.

## Deliverables

- Report generator.
- Streamlit dashboard improved.
- Final report draft.
- Demo screenshots.

## Suggested Commit Message

```text
feat(reporting): add final report and dashboard workflow
```

---

# End-of-Week Checklist

- [ ] Insight generator works.
- [ ] Final report draft created.
- [ ] Dashboard includes major sections.
- [ ] Best model documented.
- [ ] End-to-end flow tested.
- [ ] Pull Requests opened to `develop`.
- [ ] `docs/weekly_updates/week_07.md` updated.

---

# Week 7 Leads Into Week 8

Week 7 creates the final product experience.
Week 8 will focus on testing, final integration, presentation, and GitHub release.
