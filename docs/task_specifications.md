# Team Task Specifications

This document defines the main task requirements for each AutoAnalyst AI team. For step-by-step execution instructions, use [`team_step_by_step_execution_guide.md`](team_step_by_step_execution_guide.md).

## Shared Requirements for All Teams

Every team must:

- Work on its assigned feature branch.
- Keep Pull Requests focused and target `develop`.
- Update documentation when behavior or outputs change.
- Add tests when changing Python code.
- Add manual verification notes when tests are not practical.
- Keep outputs compatible with the central pipeline in `src/autoanalyst/pipeline.py`.
- Update the correct weekly progress file in `docs/weekly_updates/`.

## Team 1 â€” Project Management & GitHub / System Integration

**Members:** Mohamed Gharieb
**Branch:** `feature/project-management`

### Goal

Keep the project professionally organized, manage GitHub workflow, and coordinate system integration between teams.

### Detailed Tasks

- Maintain project documentation consistency.
- Confirm branch names and PR target rules.
- Create and organize GitHub Issues.
- Review Pull Requests for workflow, documentation, and integration readiness.
- Track weekly progress and blockers.
- Coordinate central pipeline integration across team outputs.
- Prepare final contribution and release summaries.

### Expected Outputs

- Updated planning and workflow documentation.
- Clear issue/task tracking.
- Weekly progress summaries.
- Integration checklist and release readiness notes.

### Done When

- Every team has a clear task and branch.
- PR workflow is documented and followed.
- Integration blockers are visible and assigned.
- Documentation is consistent across README and `docs/`.

## Team 2 â€” Data Understanding & Profiling

**Members:** Ø­Ø§Ø²Ù… + Ù…Ø­Ù…ÙˆØ¯ Ù…Ø§Ù‡Ø±
**Branch:** `feature/data-profiling`

### Goal

Make dataset understanding and profiling reliable for downstream analysis.

### Detailed Tasks

- Select or confirm the project dataset.
- Create and maintain `docs/data_dictionary.md`.
- Improve CSV/Excel loading behavior.
- Add validation for empty datasets and invalid files.
- Build column-level profiling outputs:
  - Data type
  - Missing count
  - Missing percentage
  - Unique count
  - Duplicate count
  - Basic numeric summary where useful
- Document data quality limitations and suggested cleaning decisions.
- Add tests under `tests/` where applicable.

### Expected Outputs

- Dataset overview.
- Data dictionary.
- Profiling module output.
- Missing values report.
- Duplicate report.
- Tests or manual verification notes.

### Done When

- Loading works for supported CSV/Excel files.
- Bad inputs return clear errors.
- Profiling output is structured and documented.
- Team 3, Team 4, and Team 7 can use the outputs.

## Team 3 â€” EDA & Visualization

**Members:** Ø£ÙŠÙ‡ + Ø¢ÙŠÙ‡ Ø¹Ù…Ø§Ø¯
**Branch:** `feature/eda-visualization`

### Goal

Create useful exploratory summaries and charts that explain the dataset.

### Detailed Tasks

- Review the dataset dictionary and profiling report.
- Define EDA questions for target, numeric, and categorical columns.
- Add numeric summary helpers.
- Add categorical summary helpers.
- Add correlation matrix helper improvements.
- Add visualization functions for:
  - Histograms
  - Bar charts
  - Box plots
  - Correlation heatmap
  - Target distribution
- Save useful chart outputs under `reports/figures/` when appropriate.
- Document key EDA findings and recommended next steps.

### Expected Outputs

- EDA helper functions.
- At least three chart types.
- EDA notes or plan.
- Chart files or dashboard-ready chart functions.
- Tests or manual verification notes.

### Done When

- EDA functions run on the selected dataset.
- Visualizations render without errors.
- Findings are clear enough for reporting and modeling decisions.

## Team 4 â€” Preprocessing & Feature Engineering

**Members:** Ø¨Ø³Ù…Ù‡ + Ø±Ø¶ÙˆÙŠ
**Branch:** `feature/preprocessing-features`

### Goal

Prepare clean, model-ready data using documented preprocessing and feature engineering steps.

### Detailed Tasks

- Review profiling and EDA notes.
- Improve missing value handling strategies.
- Add duplicate handling when needed.
- Add categorical encoding.
- Add numeric scaling when useful.
- Add datetime feature extraction.
- Create reusable preprocessing functions.
- Return clean outputs without unexpectedly mutating the original DataFrame.
- Document preprocessing decisions.
- Add tests under `tests/`.

### Expected Outputs

- Cleaning functions.
- Preprocessing helpers.
- Feature engineering functions.
- Transformation notes.
- Tests or manual verification notes.

### Done When

- Cleaned data can be passed to modeling functions.
- Feature outputs are deterministic and documented.
- Tests cover basic missing-value, encoding, and feature creation paths.

## Team 5 â€” Machine Learning

**Members:** Ø§Ù„ÙƒÙˆÙ…ÙŠ + Ø§Ù„Ø´Ø§ÙŠØ¨
**Branch:** `feature/modeling`

### Goal

Train baseline machine learning models and compare their results clearly.

### Detailed Tasks

- Confirm whether the problem is classification or regression.
- Validate that model inputs are clean and numeric.
- Improve classification model wrapper.
- Improve regression model wrapper.
- Add at least two baseline model options where suitable.
- Add model comparison helper.
- Return model name, predictions, metrics-ready outputs, and notes.
- Document expected input format.
- Add tests for basic classification/regression paths.

### Expected Outputs

- Baseline classification model.
- Baseline regression model.
- Model comparison result.
- Modeling notes.
- Tests or manual verification notes.

### Done When

- Models train on clean features.
- Predictions are available for evaluation.
- Model comparison output is structured and easy to display.

## Team 6 â€” Evaluation & Insights

**Members:** Ø³Ù‡Ø§Ø¯ + Ù…Ø±ÙˆØ©
**Branch:** `feature/evaluation-insights`

### Goal

Evaluate model outputs and generate clear insights and recommendations.

### Detailed Tasks

- Add classification evaluation metrics:
  - Accuracy
  - Precision
  - Recall
  - F1-score
  - Confusion matrix
- Add regression evaluation metrics:
  - MAE
  - MSE or RMSE
  - RÂ²
- Format evaluation results as dictionaries or DataFrames.
- Create insight generation helpers based on metrics and profiling outputs.
- Write beginner-friendly recommendation text.
- Keep insights grounded in available results.
- Add tests for classification and regression metrics.

### Expected Outputs

- Evaluation module.
- Metric tables or dictionaries.
- Insight generator.
- Recommendation bullets.
- Tests or manual verification notes.

### Done When

- Evaluation metrics are correct and readable.
- Insights are clear, practical, and not exaggerated.
- Team 7 can display evaluation and insight outputs.

## Team 7 â€” Reporting & Dashboard

**Members:** ÙŠÙ…Ù†ÙŠ + Ù…Ø­Ù…Ø¯ ÙƒÙ…Ø§Ù„
**Branch:** `feature/reporting-dashboard`

### Goal

Deliver a polished dashboard and report workflow for the final demo.

### Detailed Tasks

- Improve Streamlit dashboard layout.
- Connect dashboard to the central pipeline.
- Show dataset preview and profiling outputs.
- Display EDA charts and model/evaluation results.
- Add insight and recommendation sections.
- Improve Markdown report generation.
- Add export/download report workflow when possible.
- Add screenshots and demo instructions.
- Prepare final report and presentation outline.

### Expected Outputs

- Streamlit dashboard updates.
- Report generator integration.
- Dashboard screenshots.
- Demo guide.
- Final report or report draft.
- Manual verification notes.

### Done When

- Dashboard runs with `streamlit run app/streamlit_app.py`.
- User can upload a CSV and see useful results.
- Report output is readable and professional.
- Final demo script is ready.
