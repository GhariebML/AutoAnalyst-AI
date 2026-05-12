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
feature/data-profiling
feature/eda-analysis
feature/data-cleaning
feature/feature-engineering
feature/classification-modeling
feature/regression-modeling
feature/model-evaluation
feature/insight-report-generation
feature/dashboard-development
feature/documentation
fix/short-bug-name
docs/short-doc-update
```

Do not work directly on `main`. Avoid working directly on `develop` unless you are the Project Lead doing repository maintenance.

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

## Pull Request Checklist

Before opening a Pull Request, confirm:

- [ ] My branch is created from `develop`.
- [ ] My Pull Request targets `develop`.
- [ ] My code is readable and has meaningful names.
- [ ] I added docstrings/type hints for new Python functions.
- [ ] I updated documentation if needed.
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
