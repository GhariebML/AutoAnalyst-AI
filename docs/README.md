# AutoAnalyst AI Documentation Hub

This folder contains the professional project documentation for the AutoAnalyst AI team.

## Project Documents

| File | Purpose |
|---|---|
| `project_overview.md` | Business goal, scope, users, and expected product outcome |
| `team_delivery_plan.md` | 14-member team split into 7 two-person squads with tasks and deliverables |
| `phase_plan.md` | Project phases, milestones, and acceptance criteria |
| `agentic_architecture_langchain_langgraph.md` | Professional LangChain/LangGraph multi-agent architecture plan |
| `end_to_end_integration_strategy.md` | Central pipeline, input/output contracts, and integration rules |
| `task_specifications.md` | Detailed task requirements for each two-member squad |
| `system_architecture.md` | Technical architecture and data flow |
| `workflow.md` | Git/GitHub collaboration workflow |
| `team_roles.md` | Role responsibilities and ownership |
| `teams/` | Professional guide for each sub-team |
| `team_branch_assignments.md` | Branch naming and ownership plan |
| `roadmap.md` | High-level timeline |
| `repository_settings_guide.md` | GitHub repository configuration guide |

## Recommended Reading Order

1. `project_overview.md`
2. `end_to_end_integration_strategy.md`
3. `agentic_architecture_langchain_langgraph.md`
4. `team_delivery_plan.md`
5. `phase_plan.md`
6. `task_specifications.md`
7. `teams/README.md`
8. `workflow.md`

## Working Rule

Every team works in a feature branch, opens a Pull Request, writes tests where applicable, and updates documentation when behavior changes. Every technical contribution should connect to the central pipeline in `src/autoanalyst/pipeline.py` or clearly document the integration gap.
