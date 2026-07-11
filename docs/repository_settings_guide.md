# Repository Settings Guide

This guide explains the recommended GitHub settings for the AutoAnalyst AI repository. Some settings must be configured manually from the GitHub web UI by the repository owner or an admin.

Repository: `https://github.com/GhariebML/AutoAnalyst-AI`

## Recommended General Settings

Go to:

```text
Repository → Settings
```

Recommended configuration:

1. Confirm repository visibility is correct: public or private depending on the team's needs.
2. Enable **Issues**.
3. Enable **Discussions** if the team wants Q&A and announcements.
4. Enable **Projects** for task tracking.
5. Add collaborators with appropriate permissions.
6. Keep **Allow merge commits**, **Squash merging**, or **Rebase merging** according to the team's preference. For beginners, squash merging is often clean and simple.

## Add Collaborators

Go to:

```text
Settings → Collaborators and teams → Add people
```

Recommended permissions:

| Role | Permission |
|---|---|
| Project Lead / GitHub Manager | Admin or Maintain |
| Active developers | Write |
| Review-only members | Triage or Read |

## Protect `main` Branch

Go to:

```text
Settings → Branches → Add branch protection rule
```

Branch name pattern:

```text
main
```

Recommended options:

- Enable **Require a pull request before merging**.
- Set required approvals to **1**.
- Enable **Dismiss stale pull request approvals when new commits are pushed**.
- Enable **Require conversation resolution before merging**.
- Enable **Require status checks to pass before merging** after CI is working.
- Select the CI check once it appears, usually named `Python checks`.
- Disable force pushes.
- Disable deletions.
- Do not allow direct pushes to `main`.

## Protect `develop` Branch

Go to:

```text
Settings → Branches → Add branch protection rule
```

Branch name pattern:

```text
develop
```

Recommended options:

- Enable **Require a pull request before merging**.
- Set required approvals to **1**.
- Enable **Require conversation resolution before merging**.
- Optionally require status checks after CI is confirmed working.
- Disable force pushes.
- Disable deletions.

## Pull Request Settings

Go to:

```text
Settings → General → Pull Requests
```

Recommended:

- Allow squash merging for a clean history.
- Automatically delete head branches after merge.
- Keep Pull Request templates enabled by storing `.github/pull_request_template.md`.

## Issue Templates

Issue templates are already stored in:

```text
.github/ISSUE_TEMPLATE/
```

The team should use:

- Bug report
- Feature request
- Task
- Documentation update

## CODEOWNERS

The repository includes:

```text
.github/CODEOWNERS
```

Replace placeholder usernames such as `@eda-member` with real GitHub usernames. After branch protection is enabled, CODEOWNERS can help request the correct reviewers automatically.

## Suggested Project Board Columns

If GitHub Projects is enabled, create columns/statuses like:

1. Backlog
2. Ready
3. In Progress
4. In Review
5. Done

## Recommended Team Rule

No one should push directly to `main`. All completed work should move:

```text
feature branch → Pull Request → develop → final release Pull Request → main
```
