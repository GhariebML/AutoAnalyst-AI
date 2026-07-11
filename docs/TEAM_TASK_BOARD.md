# Team Task Board

Use this board to track Phase 1 collaboration work.

| Task ID | Owner | Branch | Component | Files | Status | PR Link | Notes |
|---|---|---|---|---|---|---|---|
| T01 | Gharieb (@GhariebML) | `feature/schemas` | Shared schemas | `src/adpilot/schemas/agent_schemas.py` | Not started | TBD | Schema changes require Team Lead approval |
| T02 | Gharieb (@GhariebML) | `feature/orchestrator` | Orchestrator | `src/adpilot/orchestration/orchestrator.py` | Not started | TBD | Keep Phase 1 scope clear |
| T03 | Gharieb (@GhariebML) | `feature/strategy-agent` | Strategy Agent | `src/adpilot/agents/strategy_agent.py`, `src/adpilot/prompts/strategy_system_prompt.md` | Not started | TBD | Depends on strategy schemas |
| T04 | Awni (@Mo-Ghaith) | `feature/research-agent` | Research Agent | `src/adpilot/agents/research_agent.py`, `src/adpilot/prompts/research_system_prompt.md` | Not started | TBD | Must return `ResearchAgentOutput` later |
| T05 | Sleem (@Sleem13) | `feature/content-agent` | Content Agent | `src/adpilot/agents/content_agent.py`, `src/adpilot/prompts/content_system_prompt.md` | Not started | TBD | Must respect content schemas |
| T06 | Khaled (@mohamedkhaledmahmoud97-ux) | `feature/analytics-agent` | Analytics Agent | `src/adpilot/agents/analytics_agent.py`, `src/adpilot/prompts/analytics_system_prompt.md` | Not started | TBD | Must validate scores and predictions |
| T07 | Karem (@mohamedkarem20) | `feature/design-agent` | Design Agent | `src/adpilot/agents/design_agent.py`, `src/adpilot/prompts/design_system_prompt.md` | Not started | TBD | Must validate image formats and briefs |
| T08 | All | Member branch | Tests and sample JSON validation | `tests/`, `data/samples/` | Not started | TBD | Every PR must include test evidence |

## Branch Rules

- Create feature branches from `develop`.
- Open all PRs into `develop`.
- Do not push directly to `main` or `develop`.
- `main` is only for stable releases.
- Shared schema changes require Team Lead approval.

## Status Values

Use one of:

- Not started
- In progress
- In review
- Changes requested
- Merged
- Blocked
