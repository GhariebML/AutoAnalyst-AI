# Team 1 — Project Management & GitHub

## Members

- Mohamed Gharieb

## Main Mission

Team 1 owns project organization, GitHub workflow, issue tracking, Pull Request quality, documentation coordination, and release readiness.

## Assigned Branch

```text
feature/project-management
```

## Main Folders

```text
docs/
.github/
```

## Core Responsibilities

- Maintain the GitHub collaboration workflow.
- Create and organize issues for each week.
- Track weekly progress and blockers.
- Review Pull Requests for structure, clarity, and completeness.
- Ensure teams work on correct branches.
- Keep project documentation organized and consistent.
- Prepare release checklists and final project status summaries.

## End-to-End Integration Duty

Team 1 must verify that every PR explains how the change fits into the full pipeline:

```text
Dataset Upload → Loading → Profiling → EDA → Cleaning → Features → Modeling → Evaluation → Insights → Report → Dashboard
```

PRs should not be approved if they create disconnected work without an integration note.

## Weekly Focus

| Week | Focus |
|---|---|
| 1 | Repository setup, branches, issues, onboarding |
| 2 | Monitor profiling work and issue progress |
| 3 | Review EDA PRs and integration notes |
| 4 | Coordinate preprocessing/modeling compatibility |
| 5 | Organize code review for feature/model work |
| 6 | Check evaluation quality and test status |
| 7 | Prepare final integration checklist |
| 8 | Final release readiness, issue cleanup, demo support |

## Step-by-Step Execution Guide

Team 1 uses the shared step-by-step execution guide for GitHub workflow, documentation review, issue tracking, PR review, and system integration coordination.

Detailed instructions are available in:

```text
docs/team_step_by_step_execution_guide.md
```

Before opening a Pull Request, each team should confirm:

- The assigned task is complete.
- The changed files match the team responsibility.
- Outputs are documented for downstream teams.
- Tests or manual verification notes are included.
- The Pull Request targets `develop`.

## Expected Deliverables

- GitHub Issues and milestones.
- Project board updates if used.
- Weekly coordination notes.
- PR review notes.
- Final release checklist.
- Updated documentation index.

## Definition of Done

- Issues are clear and assigned.
- PRs target `develop`.
- Team updates are present in `docs/weekly_updates/`.
- Integration notes are included in technical PRs.
- Validation evidence is included before merge.

## Suggested Commit Messages

```text
docs(project): update weekly coordination notes
docs(github): improve pull request workflow
chore(project): prepare release checklist
```
