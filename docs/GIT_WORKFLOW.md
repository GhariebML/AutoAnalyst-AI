# Git Workflow

AdPilot uses a Pull Request workflow with `develop` as the integration branch and `main` as the stable release branch.

## Repository

```powershell
git clone https://github.com/GhariebML/ADPilot.git
cd ADPilot
```

## Team Branch Assignments

| Member | GitHub Username | Branch |
|---|---|---|
| Gharieb | @GhariebML | `feature/schemas`, `feature/orchestrator`, `feature/strategy-agent` |
| Awni | @Mo-Ghaith | `feature/research-agent` |
| Sleem | @Sleem13 | `feature/content-agent` |
| Khaled | @mohamedkhaledmahmoud97-ux | `feature/analytics-agent` |
| Karem | @mohamedkarem20 | `feature/design-agent` |

## Start a Task

Always create your branch from `develop`:

```powershell
git checkout develop
git pull origin develop
git checkout -b feature/your-agent-name
```

Examples:

```powershell
git checkout -b feature/research-agent
git checkout -b feature/content-agent
git checkout -b feature/analytics-agent
git checkout -b feature/design-agent
```

## Daily Workflow

```powershell
git checkout develop
git pull origin develop
git checkout feature/your-agent-name
git merge develop
# work on assigned files
ruff check .
pytest -q
git add .
git commit -m "Clear commit message"
git push -u origin feature/your-agent-name
```

## Pull Request Rules

- Every PR must target `develop`.
- PR title must be clear.
- PR description must explain what changed.
- PR must mention the related agent/component.
- PR must include testing evidence (`ruff check .`, `pytest -q`).
- PR must not modify unrelated files.
- PR must not include `.env` files, API keys, tokens, or secrets.
- Shared schema changes require Team Lead approval before merge.

## Merge Rules

- Only the Team Lead merges PRs.
- Never merge failing tests.
- Never merge code that breaks Pydantic schema validation.
- Use Squash and Merge or Merge Commit based on repository policy.
- `develop` merges into `main` only after Phase 1 is stable.

## Branch Rules

- No direct commits to `main`.
- No direct commits to `develop`.
- All feature branches must be created from `develop`.
- `main` is only for stable releases.
