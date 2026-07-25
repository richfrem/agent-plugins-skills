---
name: issue-worktree-agent
plugin: dev-utils
description: >
  Skill for creating and managing isolated git worktrees (`.worktrees/issue-NNN`) for issue execution branches.
  USE ONLY when setting up or cleaning up isolated git worktrees for specific issue execution.
  DO NOT USE for managing local task files (use `task-agent`) or escalating tasks to issues (use `github-issue-backlog-agent`).
allowed_tools:
  - run_command
  - view_file
  - write_to_file
  - replace_file_content
  - multi_replace_file_content
  - grep_search
  - list_dir
---

# Issue Worktree Agent (`issue-worktree-agent`)

> **Routing Directive:** USE ONLY when setting up, listing, or removing isolated git worktrees (`.worktrees/issue-NNN`) for issue execution branches. DO NOT USE for managing local scratch tasks (use `task-agent` instead) or managing GitHub PR lifecycles (use `issue-pr-lifecycle-agent` instead).

The `issue-worktree-agent` skill manages isolated workspace environments using `git worktree`. It ensures agent work on specific issues takes place in isolated branches under `.worktrees/issue-NNN` without dirtying or interfering with the main working directory.

---

## Safety & Security Contracts

1. **Path Isolation:** All worktrees created by this skill are strictly scoped within `.worktrees/issue-NNN`.
2. **Branch Management:** Automatically creates feature branches named `issue-NNN` (or a custom branch name) off a specified base branch (default: `main`).
3. **Safe Cleanup:** Worktree removal requires explicit call; supports `--force` flag for uncommitted change cleanup.

---

## Usage catalog

### Create, List, and Remove Worktrees

- **Helper Script:** `plugins/dev-utils/skills/issue-worktree-agent/scripts/issue_worktree_manage.py`
- **CLI Usage:**
  ```bash
  # Create a worktree for Issue #123:
  python3 plugins/dev-utils/skills/issue-worktree-agent/scripts/issue_worktree_manage.py create --issue 123 --base main

  # List active worktrees:
  python3 plugins/dev-utils/skills/issue-worktree-agent/scripts/issue_worktree_manage.py list

  # Remove a worktree for Issue #123:
  python3 plugins/dev-utils/skills/issue-worktree-agent/scripts/issue_worktree_manage.py remove --issue 123
  ```

---

## Python API Interface

```python
from plugins.dev_utils.skills.issue_worktree_agent.scripts.issue_worktree_manage import (
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
