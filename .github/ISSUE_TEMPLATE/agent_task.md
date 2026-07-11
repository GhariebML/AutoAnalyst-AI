---
name: Agent Task
about: Task for implementing or updating an agent
title: "[Agent] <AgentName> - <Short description>"
labels: agent, enhancement
assignees: ""
---

**Agent Name**
(e.g., StrategyAgent, ResearchAgent)

**Owner**
@YOUR_GITHUB_USERNAME

**Objective**
What does this agent need to accomplish in Phase 1?

**Input Schema**
(Refer to schema file: `src/adpilot/schemas/agent_schemas.py`)
- Input model: `<Agent>Input`

**Output Schema**
- Output model: `<Agent>Output`

**Files to Modify/Created**
- `src/adpilot/agents/<agent>_agent.py`
- `tests/test_<agent>_agent.py`
- (Optional) Update `docs/TEAM_TASKS.md`

**Acceptance Criteria**
- [ ] Agent class inherits `BaseAgent`.
- [ ] `name`, `input_model`, `output_model` set correctly.
- [ ] `async run()` method exists and raises `NotImplementedError`.
- [ ] At least one test validates schema compliance.
- [ ] `ruff check` passes.
- [ ] `pytest` passes.

**Tests Required**
Describe what tests should be added.

**Notes**
Any additional context.
