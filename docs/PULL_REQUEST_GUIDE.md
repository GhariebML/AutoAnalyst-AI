# Pull Request Guide

All team contributions must be reviewed through Pull Requests.

## Target Branch

All feature PRs must target:

```text
develop
```

Do not open feature PRs directly into `main`.

## PR Ownership

| Area | Reviewer / Owner |
|---|---|
| Schemas, core, orchestrator | @GhariebML |
| Strategy Agent | @GhariebML |
| Research Agent | @Mo-Ghaith, review by @GhariebML |
| Content Agent | @Sleem13, review by @GhariebML |
| Analytics Agent | @mohamedkhaledmahmoud97-ux, review by @GhariebML |
| Design Agent | @mohamedkarem20, review by @GhariebML |
| Documentation and GitHub config | @GhariebML |

## Before Opening a PR

```powershell
git checkout develop
git pull origin develop
git checkout feature/your-agent-name
git merge develop
ruff check .
pytest -q
git push -u origin feature/your-agent-name
```

## PR Requirements

- Clear title.
- Description mentions what changed.
- Related agent/component is named.
- Testing evidence is included.
- No unrelated files are modified.
- No `.env`, API keys, or secrets are committed.
- Shared schema changes are approved by Team Lead.
- JSON samples and outputs remain valid.

## Merge Requirements

- Team Lead approval required.
- CI must pass.
- Conversations must be resolved.
- No breaking Pydantic schema validation.
- No direct push to `main` or `develop`.

## Stable Release PR

When Phase 1 is stable, Team Lead opens a PR:

```text
develop → main
```

This PR should include a summary of all merged features and final validation results.
