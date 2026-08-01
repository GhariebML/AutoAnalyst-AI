# Squad Task Specifications

## Squad 1 - Project Management, GitHub, Documentation

### Goal

Keep the project professionally organized and easy for all members to contribute to.

### Detailed Tasks

- Update README with current project scope.
- Maintain `docs/README.md` as the documentation index.
- Create GitHub issues for all squads.
- Verify branch naming and PR template usage.
- Prepare final contribution summary.

### Done When

- Documentation is complete and consistent.
- Every squad has a clear issue/task.
- Final report explains what each squad delivered.

## Squad 2 - Data Loading and Profiling

### Goal

Make dataset ingestion and profiling reliable.

### Detailed Tasks

- Improve `load_csv` and `load_excel`.
- Add validation for empty datasets.
- Add column-level profile: dtype, missing count, missing percent, unique count.
- Add tests under `tests/`.

### Done When

- Loading works for CSV and Excel.
- Bad inputs return clear errors.
- Profiling output is documented and tested.

## Squad 3 - EDA and Visualization

### Goal

Create useful exploratory summaries and charts.

### Detailed Tasks

- Add categorical summary helper.
- Add correlation matrix helper improvements.
- Add visualization functions for histograms, bar charts, and correlation heatmap.
- Update EDA notebook with sample findings.

### Done When

- EDA module returns clear outputs.
- At least 3 visualization types are available.
- Notebook demonstrates the workflow.

## Squad 4 - Preprocessing and Feature Engineering

### Goal

Prepare clean, model-ready data.

### Detailed Tasks

- Improve missing value strategies.
- Add column normalization option.
- Add categorical encoding.
- Add datetime features.
- Create a reusable preprocessing function.

### Done When

- Cleaning functions are tested.
- Feature functions are tested.
- Output does not mutate original DataFrame unexpectedly.

## Squad 5 - Modeling and Evaluation

### Goal

Train and evaluate baseline ML models.

### Detailed Tasks

- Improve classification model wrapper.
- Improve regression model wrapper.
- Add model comparison helper.
- Add evaluation result formatting.
- Document expected input format.

### Done When

- Models train on clean numeric features.
- Evaluation metrics are returned as dictionaries/dataframes.
- Tests cover basic classification/regression paths.

## Squad 6 - LangChain/LangGraph Agents

### Goal

Build the first professional agentic workflow for AutoAnalyst AI.

### Detailed Tasks

- Create `src/autoanalyst/agents/` structure.
- Define `AutoAnalystState`.
- Wrap existing functions as tools/nodes.
- Build LangGraph flow from intake to report.
- Add dry-run example using sample CSV.

### Done When

- Graph can run deterministic workflow without API keys.
- Optional LLM hooks are documented but safe.
- State output includes profile, insights, and report path.

## Squad 7 - Dashboard, Reporting, and Final Presentation

### Goal

Deliver a polished user-facing demo.

### Detailed Tasks

- Improve Streamlit layout.
- Connect dashboard to profile, EDA, cleaning, insights, and report generation.
- Add export report button.
- Prepare final project report and presentation outline.

### Done When

- Dashboard runs with `streamlit run app/streamlit_app.py`.
- User can upload a CSV and see useful results.
- Final demo script is ready.
