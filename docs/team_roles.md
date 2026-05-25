# Team Roles - 14 Members / 7 Squads

AutoAnalyst AI is organized into 7 squads. Each squad has 2 members and owns one major project workstream.

| Squad | Members | Role | Responsibilities | Expected Deliverables | Branch |
|---|---|---|---|---|---|
| 1 | Member 1, Member 2 | Project Management, GitHub, Documentation | Repo organization, issues, PR workflow, documentation quality, final checklist | Docs hub, issues, roadmap, final contribution summary | `docs/project-management` |
| 2 | Member 3, Member 4 | Data Loading and Profiling | CSV/Excel loading, validation, profiles, missing/duplicate reports | Loader improvements, profiling reports, tests | `feature/data-loading-profiling` |
| 3 | Member 5, Member 6 | EDA and Visualization | Numeric/categorical analysis, charts, EDA notebook | EDA functions, charts, notebook findings | `feature/eda-visualization` |
| 4 | Member 7, Member 8 | Preprocessing and Feature Engineering | Missing values, duplicates, encoding, datetime features, preprocessing pipeline | Cleaning and feature modules, tests | `feature/preprocessing-features` |
| 5 | Member 9, Member 10 | Modeling and Evaluation | Classification, regression, model comparison, metrics | Model wrappers, evaluation module, tests | `feature/modeling-evaluation` |
| 6 | Member 11, Member 12 | LangChain/LangGraph Agent System | Agent design, graph state, orchestration, tool wrapping, deterministic dry run | Agent architecture, graph code, state schema, dry-run example | `feature/agentic-workflow` |
| 7 | Member 13, Member 14 | Dashboard, Reporting, Final Presentation | Streamlit app, report export, UI polish, demo, presentation | Dashboard, generated report, final demo script | `feature/dashboard-reporting` |

## Team Operating Model

- Each squad works on one branch.
- Each squad opens Pull Requests into `develop` if available, otherwise into the agreed integration branch.
- Each Pull Request must explain what changed, how it was tested, and any limitations.
- Python code changes should include tests where practical.
- Documentation must be updated when behavior or usage changes.

## Daily Update Format

```text
Squad:
Done:
Next:
Blockers:
Needs review from:
```

## Review Ownership

- Squad 1 reviews docs and workflow consistency.
- Squads 2-5 review technical correctness of pipeline modules.
- Squad 6 reviews agent integration design.
- Squad 7 reviews dashboard usability and final presentation quality.
