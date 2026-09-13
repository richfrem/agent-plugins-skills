# GitHub Issue Worktree Management Guide

## Safety & Security Contracts

1. **Path Isolation:** All worktrees created by this skill are strictly scoped within `.worktrees/issue-NNN`.
2. **Branch Management:** Automatically creates feature branches named `issue-NNN` (or a custom branch name) off a specified base branch (default: `main`). Note: this defaults to the local `main` ref, not a freshly-fetched `origin/main` — see `plugins/agent-agentic-os/references/worktree-reconciliation-and-multi-worktree-practices.md` §2 for why a stale local base can cause lost/undone work with concurrent worktrees. Fetch `origin/main` and pass it as `base_branch` explicitly for safety until this default is hardened.
3. **Safe Cleanup:** Worktree removal requires explicit call; supports `--force` flag for uncommitted change cleanup.

---

## Python API Interface

```python
from plugins.dev_utils.skills.github_issue_worktree_agent.scripts.issue_worktree_manage import (
    create_worktree,
    list_worktrees,
    remove_worktree,
)

# Create worktree
res = create_worktree(issue_number=123, branch_name="fix-issue-123", base_branch="main")

# List worktrees
worktrees = list_worktrees()

# Remove worktree
remove_worktree(issue_number=123, force=False)
```
