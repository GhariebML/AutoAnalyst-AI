# Collaborator Invitation Guide

Repository: https://github.com/GhariebML/ADPilot.git

Because the repository is owned by `GhariebML`, do **not** add `GhariebML` as a collaborator. The owner already has full access.

## Required Collaborators

| Member | GitHub Username | Permission |
|---|---|---|
| Awni | `Mo-Ghaith` | Write |
| Sleem | `Sleem13` | Write |
| Khaled | `mohamedkhaledmahmoud97-ux` | Write |
| Karem | `mohamedkarem20` | Write |

## A. GitHub UI Method

1. Open the repository: https://github.com/GhariebML/ADPilot
2. Go to **Settings**.
3. Go to **Collaborators and teams**.
4. Click **Add people**.
5. Add these usernames:
   - `Mo-Ghaith`
   - `Sleem13`
   - `mohamedkhaledmahmoud97-ux`
   - `mohamedkarem20`
6. Give each user **Write** permission.
7. Ask each person to accept the invitation from GitHub.

## B. GitHub CLI Method

If GitHub CLI is installed, authenticated, and your account has repository admin/maintain permissions, use:

```powershell
gh repo add-collaborator Mo-Ghaith --repo GhariebML/ADPilot --permission push
gh repo add-collaborator Sleem13 --repo GhariebML/ADPilot --permission push
gh repo add-collaborator mohamedkhaledmahmoud97-ux --repo GhariebML/ADPilot --permission push
gh repo add-collaborator mohamedkarem20 --repo GhariebML/ADPilot --permission push
```

Do not include `GhariebML` in the add-collaborator commands because `GhariebML` owns the repository.

## Verify GitHub CLI Authentication

```powershell
gh auth status
```

If authentication is missing:

```powershell
gh auth login
```

## Verify Repository Access

```powershell
gh repo view GhariebML/ADPilot
gh api repos/GhariebML/ADPilot/collaborators
```

## Notes

- Use **Write** permission for team contributors.
- Use **Maintain** or **Admin** only for trusted project leads if needed.
- Collaborators must accept the GitHub invitation before they can push branches.
