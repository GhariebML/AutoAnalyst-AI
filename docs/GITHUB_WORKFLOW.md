# GitHub Workflow

## Branch Strategy

- `main`: stable branch for reviewed work.
- `develop`: optional integration branch for team coordination.
- `feature/<short-description>`: active development branches.
- `fix/<short-description>`: bug fix branches.
- `docs/<short-description>`: documentation-only branches.

Do not push directly to `main` during normal collaboration. Use pull requests.

## Create a Feature Branch

```powershell
git checkout main
git pull origin main
git checkout -b feature/my-change
```

## Commit Changes

Review changes before staging:

```powershell
git status
git diff
```

Stage intentionally:

```powershell
git add README.md docs/ src/ tests/
git commit -m "feat(agent): add structured output support"
```

## Push Changes

```powershell
git push -u origin feature/my-change
```

## Open a Pull Request

1. Open the branch on GitHub.
2. Create a pull request into `main` or the agreed integration branch.
3. Include a clear summary, tests run, and any risks.
4. Request review from the relevant teammate.
5. Merge only after checks and review pass.

## Commit Message Style

Use concise conventional-style messages:

- `feat(scope): add new capability`
- `fix(scope): correct broken behavior`
- `docs(scope): update documentation`
- `test(scope): add or improve tests`
- `refactor(scope): improve structure without behavior change`
- `chore(scope): update tooling or maintenance files`

## Safety Rules

- Never commit `.env`, API keys, tokens, passwords, or private certificates.
- Never force push unless the team explicitly agrees.
- Never overwrite remote work without fetching and reviewing first.
- Keep pull requests focused and reviewable.
- Run `ruff check .`, `pytest -q`, and relevant frontend checks before opening a PR.

