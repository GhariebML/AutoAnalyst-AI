# Team Start Message

Hi team 👋

The AdPilot repository is ready for Phase 1 collaboration.

Repository:
https://github.com/GhariebML/ADPilot.git

Please accept your GitHub collaborator invitation first, then follow these steps.

## Initial Setup

```powershell
git clone https://github.com/GhariebML/ADPilot.git
cd ADPilot
git checkout develop
git pull origin develop
```

## Create Your Feature Branch

Awni — Research Agent:

```powershell
git checkout -b feature/research-agent
```

Sleem — Content Agent:

```powershell
git checkout -b feature/content-agent
```

Khaled — Analytics Agent:

```powershell
git checkout -b feature/analytics-agent
```

Karem — Design Agent:

```powershell
git checkout -b feature/design-agent
```

Gharieb — Team Lead tasks:

```powershell
git checkout -b feature/schemas
# or
git checkout -b feature/orchestrator
# or
git checkout -b feature/strategy-agent
```

## Before You Push

Run these checks:

```powershell
ruff check .
pytest -q
```

## Push Your Branch

```powershell
git push -u origin feature/your-branch-name
```

Then open a Pull Request into `develop`.

## Important Rules

- Do not push directly to `main` or `develop`.
- All feature branches must be created from `develop`.
- All PRs must target `develop`.
- Do not change shared schemas without Gharieb’s approval.
- Do not commit `.env`, API keys, tokens, or secrets.
- Include testing evidence in your PR description.

Let’s keep the workflow clean and professional. 🚀
