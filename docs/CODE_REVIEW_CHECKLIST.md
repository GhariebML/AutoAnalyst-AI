# Code Review Checklist

This checklist is used by the Team Lead when reviewing Pull Requests.

## General
- [ ] PR title and description are clear.
- [ ] PR targets the correct branch (`develop`).
- [ ] No unrelated files changed.
- [ ] Commit history is clean (squash if needed).
- [ ] No merge conflicts.

## Code Quality
- [ ] Python code follows PEP8 (verified by `ruff check .`).
- [ ] Async methods are used for agent run methods.
- [ ] No raw strings passed between agents (typed objects from schemas).
- [ ] No real LLM or external API calls in Phase 1.
- [ ] Placeholder code raises `NotImplementedError` where needed.

## Schema Compliance
- [ ] Input and output models match the Pydantic schemas in `src/adpilot/schemas/agent_schemas.py`.
- [ ] No modification of shared schemas without prior approval.
- [ ] New fields, if any, have proper validators.

## Testing
- [ ] At least one test file added for the agent/component.
- [ ] Tests pass (`pytest -q`).
- [ ] Tests cover schema validation and basic behavior.

## Security
- [ ] No API keys, tokens, or secrets committed.
- [ ] `.env` file is not included.
- [ ] Sample JSON files use placeholder or dummy data.

## Documentation
- [ ] Relevant documentation updated (e.g., `docs/TEAM_TASKS.md`, `docs/GIT_WORKFLOW.md`).
- [ ] Added comments where non‑obvious logic exists.

## Final Approval
- [ ] CI passes (GitHub Actions: ruff + pytest).
- [ ] Reviewer is satisfied with the changes.
- [ ] Ready to merge into `develop`.
