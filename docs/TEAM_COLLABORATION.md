# Team Collaboration Workflow

AdPilot uses a professional Pull Request workflow with `develop` as the Phase 1 integration branch and `main` as the stable release branch.

## Team Assignments

| Member | GitHub Username | Role | Branches | Components |
|---|---|---|---|---|
| Gharieb | @GhariebML | Team Lead | `feature/schemas`, `feature/orchestrator`, `feature/strategy-agent` | schemas, base agent, orchestrator, strategy agent |
| Awni | @Mo-Ghaith | Research Agent Owner | `feature/research-agent` | research agent |
| Sleem | @Sleem13 | Content Agent Owner | `feature/content-agent` | content agent |
| Khaled | @mohamedkhaledmahmoud97-ux | Analytics Agent Owner | `feature/analytics-agent` | analytics agent |
| Karem | @mohamedkarem20 | Design Agent Owner | `feature/design-agent` | design agent |

## Collaboration Rules

- All feature branches must be created from `develop`.
- All PRs must target `develop`.
- `main` is only for stable releases.
- No direct push to `main` or `develop`.
- Shared schema changes require Team Lead approval before work starts.
- Team members must not modify unrelated files in their PR.
- Do not commit `.env`, API keys, or private data.

## Daily Team Workflow

```powershell
git checkout develop
git pull origin develop
git checkout feature/your-agent-name
git merge develop
# work on assigned files
ruff check .
pytest -q
git add .
git commit -m "feat(agent): clear description"
git push -u origin feature/your-agent-name
```

## PR Review Workflow

1. Team member opens PR into `develop`.
2. PR template must be completed.
3. CI must pass.
4. Team Lead reviews.
5. Requested changes are addressed.
6. Team Lead merges after approval.

## Stable Release Workflow

Only after Phase 1 is stable:

1. `develop` is reviewed.
2. Tests and lint pass.
3. Team Lead opens PR from `develop` into `main`.
4. `main` receives only stable, reviewed, tested code.
