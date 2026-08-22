# AutoAnalyst AI — Multiagent System Completion Plan

> Status: ACTIVE · Created: 2026-08-22 · Baseline: Phase 0 landed (`f3fb3a2`), 29/29 tests green
>
> This plan operationalizes `docs/agentic_architecture_langchain_langgraph.md` (10 agents,
> state schema, phases A–D) on top of the validated roadmap.

## 0. Guiding Principles

1. **Deterministic Python functions stay the core engine** — agents *wrap* modules, they do not replace them.
2. **LLM is optional** — the system must fully run with zero API keys; rule-based fallbacks everywhere.
3. **Testable with stub LLMs** — no test ever calls a real API.
4. Never hardcode keys; read from `.env` / environment only.

## 1. Target Architecture (4 layers)

```text
┌─────────────────────────────────────────────────────────────┐
│ L4  Interface: Streamlit chat + run console + trace view     │
├─────────────────────────────────────────────────────────────┤
│ L3  Orchestration: LangGraph state machine + Supervisor      │
│     (deterministic edges first, optional LLM router)         │
├─────────────────────────────────────────────────────────────┤
│ L2  Agents: 9 specialists + supervisor (thin wrappers        │
│     around L1 tools; each can call an LLM for judgment)      │
├─────────────────────────────────────────────────────────────┤
│ L1  Tools: current modules (loader, profiler, eda, cleaner,  │
│     feature_builder, models, evaluator, insights, reporter)  │
└─────────────────────────────────────────────────────────────┘
```

## 2. Agent Roster → Existing Code Mapping

| Agent | Wraps | Status at plan time | Agent adds |
|---|---|---|---|
| Dataset Intake | `data_loading/loader.py` | exists | schema validation, type sniffing, size guards |
| Profiling | `data_profiling/profiler.py` | exists | cleaning-priority recommendations |
| EDA | `eda/analyzer.py` | thin (19 LOC) | distribution/outlier analysis, chart selection |
| Cleaning | `preprocessing/cleaner.py` | solid | proposes plan → applies on approval (HITL) |
| Feature | `feature_engineering/feature_builder.py` | solid | polynomial/ratio/date features, leakage checks |
| Modeling | `modeling/classification.py`, `regression.py` | fixed RF | model selection, CV, hyperparameter search |
| Evaluation | `evaluation/evaluator.py` | thin (22 LOC) | metric interpretation, threshold analysis |
| Insight | `insights/insight_generator.py` | basic rules | optional LLM narrative + statistical findings |
| Report | `reporting/report_generator.py` | bullets-only | full Markdown/HTML report with charts |
| Supervisor | new `agents/supervisor.py` | missing | routing, retries, failure handling, escalation |

Key insight: the multiagent system is only as smart as L1. Module hardening
(validated roadmap Phase 2) **is** the agent capability layer.

## 3. Shared State

Evolve the documented `AutoAnalystState` (TypedDict → Pydantic model):

```python
plan: CleaningPlan            # proposed-but-not-applied actions
approvals: dict[str, bool]    # human-in-the-loop decisions
messages: list[AgentMessage]  # inter-agent communication log
trace: list[NodeRun]          # node, duration, status, error
retry_counts: dict[str, int]
llm_enabled: bool             # runtime flag from env
```

`PipelineResult` remains the terminal output contract — the graph's final node
emits it so the existing Streamlit app and tests keep working.

## 4. Graph Design (staged autonomy)

- **Stage 1 — Fixed graph**: deterministic edges per the documented mermaid flow;
  supervisor handles errors/retries only.
- **Stage 2 — Conditional routing**: supervisor picks cleaning strategy from the
  profile, skips modeling without target, escalates after N retries.
- **Stage 3 — Optional LLM router**: behind `AUTOANALYST_LLM_ENABLED`; falls back
  to Stage 2 logic.

Human-in-the-loop via LangGraph `interrupt_before`: pause before Cleaning
(approve plan) and before Modeling (approve target/task). Config flag for fully
autonomous runs.

## 5. Where the LLM Adds Value (and where it does not)

| Use LLM for | Keep deterministic |
|---|---|
| Narrative insight writing | All statistics, imputation, encoding |
| Cleaning-plan justification text | Cleaning plan generation (rules) |
| Modeling advisor commentary | Training, CV, metric computation |
| Report executive summary | Report assembly, tables, charts |
| Chat Q&A over results | Everything on the critical data path |

Every LLM call: prompt in `agents/prompts.py`, fake stub in tests, rule-based
fallback, never blocks the pipeline on API failure.

## 6. Milestones

| # | Milestone | Scope | Acceptance criteria | Effort |
|---|---|---|---|---|
| M0 | Foundations | ruff/mypy/pytest-cov gates, CI matrix, `agents` extra (`langgraph`, `langchain-core`, `pydantic`, `python-dotenv`) | CI green; core installs without LLM stack | 2–3 d |
| M1 | Tool layer (doc Phase A) | `agents/tools.py` wrapping module functions as LangChain tools with schemas | Each tool unit-tested; callable without LLM | 3–4 d |
| M2 | Fixed graph (doc Phase B) | `state.py`, `graph.py`, 9 agent nodes, error accumulation | Full dry-run on `data/sample/example.csv` with and without target; trace recorded | 1 wk |
| M3 | Supervisor intelligence | Conditional routing, retry/backoff, escalation, HITL interrupts | Chaos test degrades gracefully; autonomous + HITL modes pass | 1 wk |
| M4 | Module hardening = agent skills | EDA expansion, eval metrics (F1/AUC/CM/RMSE), modeling kwargs/CV, full reporter | Agents can do more, not just chat more | 1–2 wk |
| M5 | LLM layer (doc Phase C) | Insight writer, modeling advisor, narrator behind env flag; fake-LLM tests | Flag off → zero LLM calls (asserted); flag on → narratives appear | 1 wk |
| M6 | Dashboard integration (doc Phase D) | Streamlit run console, live trace viewer, chat panel, report download | Existing app intact; agent mode is a toggle | 1 wk |
| M7 | Completeness extras | Run memory, drift-detection node, plugin registry, experiment tracking | Documented extension guide; third-party agent can register | backlog |

Recommended order: **M0 → M1 → M2** yields a working multiagent system with zero
LLM dependency (~3 weeks). M4 can run parallel with M3 (different files).

## 7. Testing Strategy

- Node tests: each agent node gets input state → assert output state slice (no LLM).
- Golden-path test: full graph on `data/sample/example.csv`.
- Stub-LLM tests: scripted fake responses; assert prompts contain required context.
- Failure injection: monkeypatch a tool to raise → assert retry/escalation.
- No-key test: suite passes with all LLM env vars unset.

## 8. Dependencies & Configuration

- New `agents` extra in `pyproject.toml`: `langgraph>=0.2`, `langchain-core>=0.3`,
  `pydantic>=2.7`, `python-dotenv>=1.0`.
- `.env.example` documents flags; `.gitignore` must cover `.env`; no real keys committed.
- Provider-agnostic model access via LangChain abstraction; chosen at runtime.

## 9. Folder Layout

```text
src/autoanalyst/agents/
├── __init__.py
├── state.py          # Pydantic state models
├── graph.py          # LangGraph assembly
├── tools.py          # LangChain tool wrappers around src/autoanalyst modules
├── prompts.py        # All prompt templates
├── supervisor.py     # Routing, retries, escalation
├── llm.py            # Provider factory + FakeLLM for tests
├── trace.py          # NodeRun records / observability helpers
└── <domain>_agent.py # One file per specialist agent
```

## 10. Risks

1. Framework churn — pin versions; keep graph logic thin over deterministic code.
2. Leakage via agent decisions — feature/model choices must fit inside CV folds.
3. Two sources of truth — `run_analysis_pipeline` vs graph; one delegates to the other, never both maintained separately.
4. LLM cost/latency in UI — cache narratives per dataset hash; stream tokens.
5. Missing quality gates — M0 must land before M2.
