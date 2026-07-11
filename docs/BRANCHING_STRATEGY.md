# Branching Strategy

## Overview
AdPilot uses a **GitHub Flow–inspired** model with an additional `develop` integration branch for Phase 1 stability.

## Branches

| Branch | Purpose | Protection |
|--------|---------|------------|
| `main` | Stable, production‑ready code. Only reviewed, tested PRs are merged here. | Required PR, status checks, approval |
| `develop` | Integration branch for ongoing Phase 1 development. All feature branches merge here first. | Required PR, status checks |
| `feature/*` | Individual agent or task work. Created from `develop`, merged back into `develop`. | No direct push |

## Branch Naming Conventions

| Member | Suggested Branches |
|--------|-------------------|
| Gharieb | `feature/schemas`, `feature/orchestrator`, `feature/strategy-agent` |
| Awni | `feature/research-agent` |
| Sleem | `feature/content-agent` |
| Khaled | `feature/analytics-agent` |
| Karem | `feature/design-agent` |

## Workflow Diagram

```
main
 └─ develop
     ├─ feature/schemas
     ├─ feature/orchestrator
     ├─ feature/strategy-agent
     ├─ feature/research-agent
     ├─ feature/content-agent
     ├─ feature/analytics-agent
     └─ feature/design-agent
```

## Rules
- 🚫 **No direct commits** to `main` or `develop`.
- ✅ Every feature branch **must** open a Pull Request into `develop`.
- ✅ `develop` is merged into `main` only when Phase 1 is stable (all tests pass, schemas finalized).
- ✅ Use `git merge develop` inside your feature branch before pushing to keep it up to date.

## Creating a Feature Branch (Windows PowerShell)
```powershell
git clone https://github.com/GhariebML/ADPilot.git
cd ADPilot
git checkout develop
git pull origin develop
git checkout -b feature/your-agent-name
```

## Checking Out an Existing Feature Branch
```powershell
git fetch origin
git checkout -b feature/your-agent-name origin/feature/your-agent-name
```
