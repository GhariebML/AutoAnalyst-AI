# Team Branch Assignments

Use this file to assign each team member to a clear responsibility and branch. Replace placeholder names with the real team member names and GitHub usernames.

| Role | Branch Name | Main Responsibility | Expected Deliverables |
|---|---|---|---|
| Project Lead / GitHub Manager | `feature/documentation` or `docs/project-management` | Manage repository, issues, Pull Requests, reviews, branch protection, and final integration | Organized GitHub repo, reviewed PRs, clean releases, updated project board |
| Data Understanding Member | `feature/data-understanding` | Understand dataset context, columns, target variable, and analysis questions | Data dictionary, dataset summary, notebook notes |
| Data Profiling Member | `feature/data-profiling` | Build profiling tools for shape, dtypes, missing values, duplicates, and quality checks | Updated `data_profiling` module, profiling report, tests |
| EDA Member | `feature/eda-analysis` | Explore data patterns using summaries, correlations, and visual analysis | EDA notebook, analyzer functions, charts saved to `reports/figures/` |
| Data Cleaning Member | `feature/data-cleaning` | Handle duplicate rows, missing values, inconsistent categories, and preprocessing rules | Cleaner functions, before/after cleaning notes, tests |
| Feature Engineering Member | `feature/feature-engineering` | Create useful features, encoding helpers, and transformation utilities | Feature builder functions, examples, tests |
| Classification Modeling Member | `feature/classification-modeling` | Build baseline classification model training workflow | Classification trainer updates, metrics, modeling notes |
| Regression Modeling Member | `feature/regression-modeling` | Build baseline regression model training workflow | Regression trainer updates, metrics, modeling notes |
| Model Evaluation Member | `feature/model-evaluation` | Improve classification and regression evaluation helpers | Evaluation metrics, validation examples, tests |
| Insight & Report Generation Member | `feature/insight-report-generation` | Convert analysis results into readable insights and Markdown reports | Insight generator, report generator updates, sample report |
| Dashboard Developer | `feature/dashboard-development` | Improve Streamlit dashboard and connect pipeline components | Dashboard pages/sections, upload flow, preview/statistics UI |
| Documentation Support | `feature/documentation` | Keep README, docs, issue guides, and workflow instructions clear | Updated docs, screenshots if needed, beginner-friendly guides |

## Notes

- All branches should be created from `develop`.
- Team members should open Pull Requests into `develop`, not directly into `main`.
- If two members need the same branch, create a more specific branch such as `feature/eda-visualizations` or `feature/eda-summary-tables`.
