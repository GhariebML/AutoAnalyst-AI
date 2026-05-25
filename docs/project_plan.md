# Professional Project Plan

## Project Goal

Build AutoAnalyst AI as a modular and agent-ready data analysis system that helps users move from raw dataset to useful insights, baseline models, and reports.

## Team Model

The 14-member team is divided into 7 squads. Each squad has 2 members and owns one project workstream.

Detailed team split:

- `docs/team_delivery_plan.md`
- `docs/task_specifications.md`
- `docs/team_roles.md`

## Delivery Phases

| Phase | Name | Main Focus |
|---|---|---|
| Phase 0 | Setup and Alignment | Repo setup, team assignment, baseline validation |
| Phase 1 | Foundation Modules | Data loading, profiling, EDA, preprocessing, modeling |
| Phase 2 | Agentic Architecture | LangChain/LangGraph workflow design and dry-run implementation |
| Phase 3 | Dashboard and Reporting | Streamlit integration and report export |
| Phase 4 | Testing and Documentation | QA, docs, final report |
| Phase 5 | Final Demo | Presentation and delivery |

Full phase details:

- `docs/phase_plan.md`

## Technical Direction

The project should keep the current Python package structure and add an optional agentic layer:

```text
src/autoanalyst/agents/
```

The agentic layer should use:

- LangChain for tools, prompts, optional LLM calls, and model abstraction.
- LangGraph for stateful workflow orchestration.
- Deterministic fallback logic so the project can run without API keys.

## Quality Gates

Before merging any squad work:

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
- Agentic LangGraph workflow prototype.
- Tests for core modules.
- Final report.
- Professional documentation folder.
- GitHub repository with clear PR workflow.
