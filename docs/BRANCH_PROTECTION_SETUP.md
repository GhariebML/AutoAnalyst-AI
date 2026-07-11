# Branch Protection Setup

Branch protection must be configured manually in GitHub unless GitHub CLI is authenticated and the current account has sufficient repository permissions.

Repository: https://github.com/GhariebML/ADPilot

Go to:

`Repository → Settings → Branches → Add branch protection rule`

## Rule 1: Protect `main`

Branch name pattern:

```text
main
```

Enable:

- Require a pull request before merging
- Require approvals: at least 1
- Dismiss stale pull request approvals when new commits are pushed
- Require review from Code Owners if available
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Select CI status checks if visible
- Require conversation resolution before merging
- Block force pushes
- Do not allow deletions

Purpose:

- `main` is only for stable releases.
- No direct development should happen on `main`.

## Rule 2: Protect `develop`

Branch name pattern:

```text
develop
```

Enable:

- Require a pull request before merging
- Require approvals: at least 1
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Require conversation resolution before merging
- Block force pushes
- Do not allow deletions

Purpose:

- `develop` is the Phase 1 integration branch.
- All feature branches must open PRs into `develop`.

## GitHub Free Repository Note

On GitHub Free personal repositories, some advanced branch protection features may depend on repository visibility or plan. If a setting is unavailable, enable the closest available option.

## Optional GitHub CLI Setup

Do not run these commands unless GitHub CLI is authenticated and permissions are confirmed.

Check authentication:

```powershell
gh auth status
```

### Optional `main` protection command

```powershell
gh api `
  --method PUT `
  -H "Accept: application/vnd.github+json" `
  /repos/GhariebML/ADPilot/branches/main/protection `
  -f required_status_checks='{"strict":true,"contexts":[]}' `
  -f enforce_admins=true `
  -f required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":true}' `
  -f restrictions=null
```

### Optional `develop` protection command

```powershell
gh api `
  --method PUT `
  -H "Accept: application/vnd.github+json" `
  /repos/GhariebML/ADPilot/branches/develop/protection `
  -f required_status_checks='{"strict":true,"contexts":[]}' `
  -f enforce_admins=false `
  -f required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' `
  -f restrictions=null
```

Important:

- Status check context names may need adjustment after GitHub Actions runs once.
- Do not force push.
- Do not disable protections after enabling them.
