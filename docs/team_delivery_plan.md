# 14-Member Team Delivery Plan

## Team Structure

The project team has 14 members. Work is divided into 7 squads. Each squad has 2 members and owns one major workstream.

> Replace `Member 1`, `Member 2`, etc. with real names after assigning the team.

| Squad | Members | Workstream | Branch | Main Output |
|---|---|---|---|---|
| Squad 1 | Member 1, Member 2 | Project Management, GitHub, Documentation | `docs/project-management` | Clean repo workflow, issues, docs, milestones |
| Squad 2 | Member 3, Member 4 | Data Loading and Data Profiling | `feature/data-loading-profiling` | Robust loaders and profiling reports |
| Squad 3 | Member 5, Member 6 | EDA and Visualization | `feature/eda-visualization` | EDA functions, charts, notebook outputs |
| Squad 4 | Member 7, Member 8 | Preprocessing and Feature Engineering | `feature/preprocessing-features` | Cleaning pipeline and feature builders |
| Squad 5 | Member 9, Member 10 | Modeling and Evaluation | `feature/modeling-evaluation` | Classification/regression training and metrics |
| Squad 6 | Member 11, Member 12 | LangChain/LangGraph Agent System | `feature/agentic-workflow` | Multi-agent workflow graph and orchestration |
| Squad 7 | Member 13, Member 14 | Dashboard, Reporting, Final Presentation | `feature/dashboard-reporting` | Streamlit app, reports, demo, final slides |

## Squad Responsibilities

### Squad 1 - Project Management, GitHub, Documentation

Owns the professional project structure and collaboration system.

Responsibilities:

- Maintain `README.md`, `docs/`, and contribution guides.
- Create and organize GitHub Issues.
- Maintain milestones and project board if used.
- Ensure branches and Pull Requests follow the workflow.
- Review documentation quality before final delivery.

Deliverables:

- Updated documentation hub.
- Clear task board.
- Final repository checklist.
- Release notes for final submission.

### Squad 2 - Data Loading and Data Profiling

Owns ingestion and dataset understanding.

Responsibilities:

- Improve CSV and Excel loaders.
- Add validation for empty files, unsupported formats, and bad paths.
- Generate dataset profiles: shape, columns, dtypes, missing values, duplicates, unique counts.
- Add tests for loaders and profiling functions.

Deliverables:

- Reliable loading module.
- Data profiling report output.
- Unit tests.
- Usage examples.

### Squad 3 - EDA and Visualization

Owns exploratory analysis.

Responsibilities:

- Add numeric and categorical summaries.
- Add correlation analysis.
- Build visualization helpers using Matplotlib/Seaborn/Plotly.
- Create EDA notebook with sample dataset findings.

Deliverables:

- EDA module functions.
- Visualization functions.
- EDA notebook.
- Charts saved under `reports/figures/` when needed.

### Squad 4 - Preprocessing and Feature Engineering

Owns data preparation.

Responsibilities:

- Improve duplicate handling.
- Improve missing-value handling.
- Add categorical encoding helpers.
- Add datetime feature extraction.
- Prepare a reusable preprocessing pipeline.

Deliverables:

- Cleaning functions.
- Feature engineering functions.
- Tests for preprocessing and feature outputs.
- Example processed dataset if appropriate.

### Squad 5 - Modeling and Evaluation

Owns machine learning baseline models.

Responsibilities:

- Improve classification wrapper.
- Improve regression wrapper.
- Add model comparison option.
- Add evaluation metrics.
- Document target-column selection and model assumptions.

Deliverables:

- Classification and regression workflows.
- Evaluation reports.
- Tests for model and metric functions.
- Example modeling notebook.

### Squad 6 - LangChain/LangGraph Agent System

Owns the agentic AI layer.

Responsibilities:

- Design agents for each analysis stage.
- Build a LangGraph workflow that routes dataset state between agents.
- Use LangChain tools/runnables where useful.
- Add clear state schema and graph nodes.
- Keep LLM usage optional and safe.

Deliverables:

- Agent architecture document.
- LangGraph state design.
- Starter agent workflow code.
- Tests or dry-run examples using deterministic functions.

### Squad 7 - Dashboard, Reporting, Final Presentation

Owns user-facing delivery.

Responsibilities:

- Improve Streamlit dashboard.
- Connect dashboard to profiling, EDA, cleaning, insights, and reporting modules.
- Add Markdown report export.
- Prepare final report and presentation.

Deliverables:

- Polished Streamlit app.
- Final Markdown report.
- Demo script.
- Final presentation outline.

## Communication Rules

- Each squad gives a short daily update: Done, Next, Blockers.
- Every code change must go through Pull Request review.
- Every squad must include tests or a manual verification note.
- No secrets, API keys, private datasets, or local paths should be committed.
