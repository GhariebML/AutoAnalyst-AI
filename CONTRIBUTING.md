# Contributing to AutoAnalyst AI

Thank you for contributing to AutoAnalyst AI. This project is designed to help the team learn professional software, data science, and GitHub collaboration practices.

## Contribution Workflow

1. Start from the latest `develop` branch.
2. Create a focused feature branch.
3. Make small, clear changes.
4. Add or update tests when changing Python code.
5. Update documentation when behavior or usage changes.
6. Push your branch to GitHub.
7. Open a Pull Request into `develop`.
8. Request review and respond politely to feedback.

## Branch Naming Rules

Use clear branch names:

```text
feature/project-management
feature/data-profiling
feature/eda-visualization
feature/preprocessing-features
feature/modeling
feature/evaluation-insights
feature/reporting-dashboard
fix/short-bug-name
docs/short-doc-update
```

Do not work directly on `main`. Avoid working directly on `develop` unless you are the Project Lead doing repository maintenance.

## Weekly Contribution Rules

Each sub-team should:

1. Pull latest changes from `develop`.
2. Work only on its assigned feature branch.
3. Commit small, clear changes.
4. Push the branch regularly.
5. Open a Pull Request into `develop`.
6. Add a weekly update in `docs/weekly_updates/week_XX.md`.
7. Mention blockers early.
8. Never push directly to `main`.

Assigned branches are documented in [`docs/team_branch_assignments.md`](docs/team_branch_assignments.md).

## Integration-Friendly Contribution Rules

AutoAnalyst AI is an end-to-end system. Every feature should connect cleanly to the central pipeline in:

```text
src/autoanalyst/pipeline.py
```

Before opening a Pull Request, contributors should confirm:

1. The change has clear inputs and outputs.
2. The change can be called from the central pipeline or has a documented reason why not yet.
3. The dashboard does not duplicate business logic from backend modules.
4. New module outputs are structured for reports, insights, dashboard display, or future agents.
5. Integration tests are added or updated when pipeline behavior changes.
6. Documentation explains how the work fits into the full workflow.

See [`docs/end_to_end_integration_strategy.md`](docs/end_to_end_integration_strategy.md).

## Commit Message Format

Use this format:

```text
type(scope): short description
```

Examples:

```text
feat(eda): add correlation heatmap function
fix(loader): handle missing file path error
docs(readme): update installation section
refactor(modeling): simplify classification trainer
test(preprocessing): add test for missing value handling
```

Recommended types:

| Type | Use For |
|---|---|
| `feat` | New functionality |
| `fix` | Bug fixes |
| `docs` | Documentation changes |
| `test` | Tests |
| `refactor` | Code cleanup without changing behavior |
| `chore` | Project setup, configuration, maintenance |

## Pull Request Expectations

Each Pull Request should include:

- Clear summary.
- Files changed.
- Related issue if available.
- Screenshots if dashboard or charts were changed.
- Checklist confirming the code was tested.
- Notes for reviewers.

## Pull Request Checklist

Before opening a Pull Request, confirm:

- [ ] My branch is created from `develop`.
- [ ] My Pull Request targets `develop`.
- [ ] My code is readable and has meaningful names.
- [ ] I added docstrings/type hints for new Python functions.
- [ ] I updated documentation if needed.
- [ ] I added or updated the weekly update file if this is weekly work.
- [ ] I confirmed my change fits the end-to-end pipeline or documented the integration gap.
- [ ] I ran `python -m compileall -q app src tests` locally if I changed Python code.
- [ ] I ran `pytest` locally if I changed Python code.
- [ ] I did not commit private files, secrets, API keys, or large raw datasets.
- [ ] I explained what changed in the PR description.

## Code Style Rules

- Keep functions short and focused.
- Use meaningful function and variable names.
- Add type hints where practical.
- Add docstrings to public functions/classes.
- Prefer simple Pandas/Scikit-learn code that beginners can understand.
- Do not hardcode local machine paths such as `C:\Users\...` or `D:\...`.
- Do not include credentials, tokens, private keys, or passwords.

## Documentation Rules

- Update README or docs when changing setup, usage, workflow, or architecture.
- Keep Markdown headings clear.
- Use code blocks for commands.
- Write beginner-friendly explanations.
- Add examples when possible.

## Reporting Bugs

Use the **Bug report** issue template. Include:

- What happened
- What you expected
- Steps to reproduce
- Error message or screenshot
- Your environment if relevant

## Requesting Features

Use the **Feature request** issue template. Include:

- What feature you want
- Why it is useful
- Suggested implementation if you have one
- Any examples or references

## Communicating Blockers

If you are blocked:

1. Open or comment on the related issue.
2. Explain what you tried.
3. Paste the exact error message if there is one.
4. Mention the Project Lead or relevant teammate.
5. Ask a specific question.

Good blocker message:

```text
I am blocked on the preprocessing module. I tried `pytest`, but `handle_missing_values` fails with object columns. Error: ... Can someone review the strategy for categorical values?
```

## Review Expectations

Reviewers should check:

- Correctness
- Readability
- Simplicity
- Tests or manual validation
- Documentation updates
- No secrets or local paths

Be kind and specific when giving feedback.
