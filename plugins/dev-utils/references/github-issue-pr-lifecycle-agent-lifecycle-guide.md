# GitHub Issue PR Lifecycle Reference Guide

## Safety & Security Contracts

1. **Dry-Run by Default:** Execution defaults to dry-run payload generation (`--execute` flag required for live changes).
2. **Linked Resolution:** Automatically appends `Closes #NNN` to PR bodies to enforce automatic resolution tracking.
3. **Structured Flow:** Sequence: Worktree Creation -> PR Submission -> Issue Closure -> Worktree Cleanup.

---

## Detailed Execution Sequence

```
[Issue #NNN]
    │
    ▼
1. Create isolated worktree (.worktrees/issue-NNN) via github-issue-worktree-agent
    │
    ▼
2. Push commits to remote tracking branch (issue-NNN)
    │
    ▼
3. Create GitHub Pull Request (`gh pr create --title ... --body ...`)
    │
    ▼
4. Verify PR creation receipt and link issue
    │
    ▼
5. Close issue upon merge/completion (`gh issue close NNN`)
    │
    ▼
6. Remove isolated worktree and clean workspace
```

---

## Python API Interface

```python
from plugins.dev_utils.skills.github_issue_pr_lifecycle_agent.scripts.issue_pr_orchestrate import (
    orchestrate_lifecycle,
    generate_lifecycle_payload,
)

# Generate dry-run payload
payload = generate_lifecycle_payload(issue_number=42, title="Fix bug", body="Fixes #42")

# Orchestrate lifecycle with execution
res = orchestrate_lifecycle(issue_number=42, title="Fix bug", body="Fixes #42", dry_run=False)
```
