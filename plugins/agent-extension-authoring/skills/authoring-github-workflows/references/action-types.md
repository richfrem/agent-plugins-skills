# Traditional GitHub Actions Reference

## When to Use This Skill vs Others

| Task | Use This Skill | Use `create-agentic-workflow` |
|---|---|---|
| Run tests on every PR | ✅ | ❌ |
| Build and publish a Docker image | ✅ | ❌ |
| Deploy to GitHub Pages | ✅ | ❌ |
| Check if PR matches the spec | ❌ | ✅ |
| Daily repo health report | ❌ | ✅ |
| Code review with AI judgment | ❌ | ✅ |

### Available Trigger Events

| Trigger | Fires when | Common for |
|---|---|---|
| `pull_request` | PR opened/updated | Tests, lint, security |
| `push` | Branch pushed | Deploy, release checks |
| `schedule` (cron) | On a time schedule | Maintenance, reports |
| `workflow_dispatch` | Manual button click | Deploys, one-off jobs |
| `release` | Release published | Package publishing |
| `issues` | Issue opened/labeled | Triage, notifications |
| `workflow_call` | Called by another workflow | Reusable sub-workflows |

### Permissions Model

```yaml
permissions:
  contents: read      # Read repo files
  contents: write     # Commit files, push
  pull-requests: write # Comment on PRs
  issues: write       # Create/update issues
  packages: write     # Publish packages
  id-token: write     # OIDC (for cloud deploys)
```

> Always declare minimum required permissions. The `GITHUB_TOKEN` grants no permissions by default unless declared.

### Common Action Patterns

```yaml
# Checkout
- uses: actions/checkout@v4

# Setup language
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"

# Cache dependencies
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}

# Upload artifacts
- uses: actions/upload-artifact@v4
  with:
    name: report
    path: output/

# Publish GitHub Release
- uses: softprops/action-gh-release@v2
  with:
    files: dist/*
```
