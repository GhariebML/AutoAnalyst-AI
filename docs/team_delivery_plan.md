# Team Delivery Plan

## Team Structure

The project is divided into 7 teams. Team 1 is handled by Mohamed Gharieb for project management, GitHub workflow, and system integration. Teams 2-7 own the main technical and delivery workstreams.

For detailed task execution steps, use [`team_step_by_step_execution_guide.md`](team_step_by_step_execution_guide.md).

| Team | Members | Workstream | Branch | Main Output |
|---|---|---|---|---|
| Team 1 | Mohamed Gharieb | Project Management & GitHub / System Integration | `feature/project-management` | Clean repo workflow, issues, docs, milestones, integration coordination |
| Team 2 | Ø­Ø§Ø²Ù… + Ù…Ø­Ù…ÙˆØ¯ Ù…Ø§Ù‡Ø± | Data Understanding & Profiling | `feature/data-profiling` | Data dictionary, robust loaders, profiling reports, data quality notes |
| Team 3 | Ø£ÙŠÙ‡ + Ø¢ÙŠÙ‡ Ø¹Ù…Ø§Ø¯ | EDA & Visualization | `feature/eda-visualization` | EDA functions, charts, findings, visualization notes |
| Team 4 | Ø¨Ø³Ù…Ù‡ + Ø±Ø¶ÙˆÙŠ | Preprocessing & Feature Engineering | `feature/preprocessing-features` | Cleaning pipeline, preprocessing helpers, feature builders |
| Team 5 | Ø§Ù„ÙƒÙˆÙ…ÙŠ + Ø§Ù„Ø´Ø§ÙŠØ¨ | Machine Learning | `feature/modeling` | Baseline models, model wrappers, model comparison output |
| Team 6 | Ø³Ù‡Ø§Ø¯ + Ù…Ø±ÙˆØ© | Evaluation & Insights | `feature/evaluation-insights` | Evaluation metrics, insight generator, recommendation notes |
| Team 7 | ÙŠÙ…Ù†ÙŠ + Ù…Ø­Ù…Ø¯ ÙƒÙ…Ø§Ù„ | Reporting & Dashboard | `feature/reporting-dashboard` | Streamlit app, reports, screenshots, demo, final slides |

## Team Responsibilities

### Team 1 â€” Project Management & GitHub / System Integration

Owns the professional project structure, collaboration system, and cross-team integration coordination.

Responsibilities:

- Maintain `README.md`, `docs/`, and contribution guides.
- Create and organize GitHub Issues.
- Maintain milestones and project board if used.
- Ensure branches and Pull Requests follow the workflow.
- Review documentation quality before final delivery.
- Confirm each team output can connect to `src/autoanalyst/pipeline.py`.

Deliverables:

- Updated documentation hub.
- Clear task board.
- Integration checklist.
- Final repository checklist.
- Release notes for final submission.

### Team 2 â€” Data Understanding & Profiling

Owns ingestion and dataset understanding.

Responsibilities:

- Select or confirm the project dataset.
- Maintain `docs/data_dictionary.md`.
- Improve CSV and Excel loaders.
- Add validation for empty files, unsupported formats, and bad paths.
- Generate dataset profiles: shape, columns, dtypes, missing values, duplicates, unique counts.
- Add tests for loaders and profiling functions.

Deliverables:

- Reliable loading module.
- Data dictionary.
- Data profiling report output.
- Data quality notes.
- Unit tests or manual verification notes.

### Team 3 â€” EDA & Visualization

Owns exploratory analysis.

Responsibilities:

- Add numeric and categorical summaries.
- Add correlation analysis.
- Build visualization helpers using Matplotlib, Seaborn, or Plotly.
- Create EDA notes with sample dataset findings.
- Save useful charts under `reports/figures/` when needed.

Deliverables:

- EDA module functions.
- Visualization functions.
- EDA findings.
- Charts saved under `reports/figures/` when needed.

### Team 4 â€” Preprocessing & Feature Engineering

Owns data preparation.

Responsibilities:

- Improve duplicate handling.
- Improve missing-value handling.
- Add categorical encoding helpers.
- Add numeric scaling when useful.
- Add datetime feature extraction.
- Prepare a reusable preprocessing pipeline.

Deliverables:

- Cleaning functions.
- Preprocessing helpers.
- Feature engineering functions.
- Tests for preprocessing and feature outputs.
- Transformation notes.

### Team 5 â€” Machine Learning

Owns machine learning baseline models.

Responsibilities:

- Confirm classification or regression task type.
- Improve classification wrapper.
- Improve regression wrapper.
- Add baseline model options.
- Add model comparison helper.
- Document target-column selection and model assumptions.

Deliverables:

- Classification workflow.
- Regression workflow.
- Model comparison output.
- Modeling notes.
- Tests for model functions.

### Team 6 â€” Evaluation & Insights

Owns model evaluation and insight generation.

Responsibilities:

- Add classification metrics: accuracy, precision, recall, F1-score, confusion matrix.
- Add regression metrics: MAE, MSE/RMSE, RÂ².
- Format metrics as dictionaries or DataFrames.
- Generate insight bullets based on profiling and evaluation outputs.
- Write clear recommendations for non-technical readers.

Deliverables:

- Evaluation module.
- Metric tables or dictionaries.
- Insight generator.
- Recommendation notes.
- Tests for metric functions.

### Team 7 â€” Reporting & Dashboard

Owns user-facing delivery.

Responsibilities:

- Improve Streamlit dashboard.
- Connect dashboard to the central pipeline.
- Display profiling, EDA, preprocessing, model, evaluation, and insight outputs.
- Add Markdown report export.
- Prepare screenshots, final report, and presentation.

Deliverables:

- Polished Streamlit app.
- Generated Markdown report.
- Dashboard screenshots.
- Demo script.
- Final presentation outline.

## Communication Rules

- Each team gives a short daily update: Done, Next, Blockers.
- Every code change must go through Pull Request review into `develop`.
- Every team must include tests or a manual verification note.
- No secrets, API keys, private datasets, or local paths should be committed.
