---
concept: traditional-github-actions-reference
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-github-action/references/action-types.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.851765+00:00
cluster: permissions
content_hash: a53e893296bc0487
---

# Traditional GitHub Actions Reference

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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


## See Also

- [[optimizer-engine-patterns-reference-design]]
- [[project-setup-reference-guide]]
- [[optimizer-engine-patterns-reference-design]]
- [[analysis-framework-reference]]
- [[path-reference-auditor---usage-guide]]
- [[path-reference-auditor]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-github-action/references/action-types.md`
- **Indexed:** 2026-04-17T06:42:09.851765+00:00
