# AutoAnalyst AI Team GitHub Workflow

This guide explains how the team should work together using Git and GitHub. Follow it step by step, especially if you are new to collaboration workflows.

## Branch Strategy

| Branch | Purpose | Who Uses It |
|---|---|---|
| `main` | Stable, production-ready project version | Project Lead only through Pull Requests |
| `develop` | Integration branch where completed team work is combined | All team members through Pull Requests |
| `feature/...` | Individual task branches created from `develop` | Each team member |

> Important: Do **not** push directly to `main`. Team work should go through feature branches and Pull Requests.

---

## 1. Clone the Repository

PowerShell or Git Bash:

```bash
git clone https://github.com/GhariebML/AutoAnalyst-AI.git
cd AutoAnalyst-AI
```

---

## 2. Create and Activate a Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
pip install -e .
```

---

## 3. Switch to `develop`

```bash
git checkout develop
git pull origin develop
```

If `develop` is not available locally yet:

```bash
git fetch origin
git checkout -b develop origin/develop
```

---

## 4. Create Your Feature Branch

Always create your branch from the latest `develop`:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-task-name
```

Example:

```bash
git checkout -b feature/data-profiling
```

---

## 5. Pull Latest Changes Before Working

Before starting work each day:

```bash
git checkout develop
git pull origin develop
git checkout feature/your-task-name
git merge develop
```

If there are conflicts, see the conflict section below.

---

## 6. Commit Changes Properly

Check your changes:

```bash
git status
```

Stage and commit:

```bash
git add .
git commit -m "type(scope): short description"
```

Good examples:

```text
feat(eda): add correlation heatmap function
fix(loader): handle missing file path error
docs(readme): update installation section
refactor(modeling): simplify classification trainer
test(preprocessing): add test for missing value handling
```

Commit types:

| Type | Meaning |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `test` | Tests |
| `refactor` | Code cleanup without changing behavior |
| `chore` | Maintenance/configuration |

---

## 7. Push Your Branch

```bash
git push origin feature/your-task-name
```

If this is your first push for the branch:

```bash
git push -u origin feature/your-task-name
```

---

## 8. Open a Pull Request

1. Open the GitHub repository.
2. Click **Pull requests**.
3. Click **New pull request**.
4. Set:
   - Base branch: `develop`
   - Compare branch: your feature branch
5. Fill the Pull Request template.
6. Link the related issue if one exists.
7. Request at least one reviewer.

---

## 9. Ask for Code Review

When asking for review, mention:

- What you changed
- Which files are important
- How you tested it
- Any known limitations or questions

Example:

```text
Please review my EDA module update. I added numeric summaries and a correlation helper. Tests pass locally with pytest.
```

---

## 10. Resolve Conflicts - Basic Method

If GitHub says your branch has conflicts:

```bash
git checkout develop
git pull origin develop
git checkout feature/your-task-name
git merge develop
```

Open the conflicted files and look for conflict markers:

```text
<<<<<<< HEAD
Your branch version
=======
Develop branch version
>>>>>>> develop
```

Edit the file so only the correct final version remains. Then:

```bash
git add .
git commit -m "fix: resolve merge conflicts"
git push origin feature/your-task-name
```

If you are unsure, ask the Project Lead before resolving conflicts.

---

## 11. Before Submitting a Pull Request

Run:

```bash
pytest
```

Also check:

```bash
git status
```

Make sure no private files, datasets, secrets, API keys, or local machine paths are committed.

---

## 12. Merge Policy

- Feature branches merge into `develop` through Pull Requests.
- `develop` merges into `main` only when the project is stable.
- At least one reviewer should approve before merging.
- Do not force push shared branches.
