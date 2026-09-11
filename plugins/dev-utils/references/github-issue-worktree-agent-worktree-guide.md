# GitHub Issue Worktree Management Guide

## Safety & Security Contracts

1. **Path Isolation:** All worktrees created by this skill are strictly scoped within `.worktrees/issue-NNN`.
2. **Branch Management:** Automatically creates feature branches named `issue-NNN` (or a custom branch name) off a specified base branch (default: `main`).
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
