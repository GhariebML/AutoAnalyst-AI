# Contributing to AdPilot

Thank you for contributing to AdPilot. This repository uses a Pull Request workflow with `develop` as the integration branch and `main` as the stable branch.

## 1. Clone the Repository

```powershell
git clone https://github.com/GhariebML/ADPilot.git
cd ADPilot
```

## 2. Create a Feature Branch

Always branch from `develop`:

```powershell
git checkout develop
git pull origin develop
git checkout -b feature/your-agent-name
```

Recommended branch names:

- `feature/schemas`
- `feature/orchestrator`
- `feature/strategy-agent`
- `feature/research-agent`
- `feature/content-agent`
- `feature/analytics-agent`
- `feature/design-agent`
- `feature/docs`

## 3. Install Dependencies

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

## 4. Run Tests

```powershell
pytest -q
```

## 5. Format and Lint

```powershell
ruff check .
black .
```

Before opening a PR, at minimum run:

```powershell
ruff check .
pytest -q
```

## 6. Open a Pull Request

1. Push your branch:
   ```powershell
   git push -u origin feature/your-agent-name
   ```
2. Open a PR into `develop`, not `main`.
3. Fill out the PR template.
4. Include testing evidence.
5. Request review from the Team Lead.

## 7. Coding Standards

- Use type hints.
- Keep methods small and clear.
- Agent interfaces should remain async.
- Agent inputs and outputs must use Pydantic schemas.
- No raw strings should be passed between agents.
- No real LLM or external API calls during Phase 1 unless approved.
- Do not modify unrelated files in your PR.

## 8. Commit Message Examples

```text
feat(strategy): add initial strategy agent structure
feat(research): implement persona output validation
fix(content): clean invalid JSON output parsing
docs(team): add PR workflow instructions
test(schemas): add funnel allocation validation test
```

## 9. Schema Change Rules

Shared schemas in `src/adpilot/schemas/agent_schemas.py` are contracts between agents.

Rules:

- Do not change shared schemas without Team Lead approval.
- Open a `Schema Change Request` issue first.
- Explain affected agents and backward compatibility impact.
- Add/update tests for every schema change.

## 10. Avoiding Merge Conflicts

Before working each day:

```powershell
git checkout develop
git pull origin develop
git checkout feature/your-agent-name
git merge develop
```

If conflicts occur:

1. Read the conflict markers carefully.
2. Keep only the correct final code.
3. Run tests after resolving.
4. Commit the merge resolution.

Never force push unless the Team Lead explicitly approves it.
