# Professional Project Plan

## Project Goal

Build AutoAnalyst AI as a modular and agent-ready data analysis system that helps users move from raw dataset to useful insights, baseline models, and reports.

## Team Model

The project is divided into 7 teams. Team 1 is Mohamed Gharieb for project management, GitHub workflow, and system integration. Teams 2-7 own the main technical and delivery workstreams.

Detailed team split:

- `docs/team_delivery_plan.md`
- `docs/task_specifications.md`
- `docs/team_roles.md`

## Delivery Phases

| Phase | Name | Main Focus |
|---|---|---|
| Phase 0 | Setup and Alignment | Repo setup, team assignment, baseline validation |
| Phase 1 | Foundation Modules | Data loading, profiling, EDA, preprocessing, modeling |
| Phase 2 | Evaluation and Insights | Model metrics, insight generation, and recommendations |
| Phase 3 | Dashboard and Reporting | Streamlit integration and report export |
| Phase 4 | Testing and Documentation | QA, docs, final report |
| Phase 5 | Final Demo | Presentation and delivery |

Full phase details:

- `docs/phase_plan.md`

## Technical Direction

The project should keep the current Python package structure and focus on a deterministic end-to-end analytics pipeline. Optional agentic features can be explored later, but the current team distribution focuses on data profiling, EDA, preprocessing, machine learning, evaluation, insights, reporting, dashboard delivery, and system integration.

## Quality Gates

Before merging any team work:

```bash
python -m compileall -q app src tests
pytest
```

Recommended additional checks later:

```bash
ruff check .
ruff format --check .
```

## Final Deliverables

- Working Python package.
- Streamlit dashboard.
- Tests for core modules.
- Final report.
- Professional documentation folder.
- GitHub repository with clear PR workflow.
