# GitHub Collaboration Workflow

## Clone the repository

```bash
git clone https://github.com/<your-org-or-username>/AutoAnalyst-AI.git
cd AutoAnalyst-AI
```

## Create a virtual environment

PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

## Install requirements

```bash
pip install -r requirements.txt
pip install -e .
```

## Create a feature branch

```bash
git checkout main
git pull origin main
git checkout -b feature/your-task-name
```

## Commit changes

```bash
git status
git add .
git commit -m "feat: add your clear change description"
```

## Push changes

```bash
git push origin feature/your-task-name
```

## Open a Pull Request

1. Open the repository on GitHub.
2. Click **Compare & pull request**.
3. Explain what changed and how it was tested.
4. Request a review from a teammate.

## Review and merge

- Review code for clarity, correctness, and documentation.
- Ask for changes when needed.
- Merge only after approval and passing checks.
- Delete merged branches to keep the repository clean.
