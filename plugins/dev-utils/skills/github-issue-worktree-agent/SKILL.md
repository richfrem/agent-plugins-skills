---
name: github-issue-worktree-agent
plugin: dev-utils
description: >
  Skill for creating and managing isolated git worktrees (`.worktrees/issue-NNN`) for issue execution branches.
  USE ONLY when setting up or cleaning up isolated git worktrees for specific issue execution.
  DO NOT USE for escalating tasks to issues (use `github-issue-backlog-agent`) or managing full PR lifecycles (use `github-issue-pr-lifecycle-agent`).
allowed_tools:
  - run_command
  - view_file
  - write_to_file
  - replace_file_content
  - multi_replace_file_content
  - grep_search
  - list_dir
---

# GitHub Issue Worktree Agent (`github-issue-worktree-agent`)

> **Routing Directive:** USE ONLY when setting up, listing, or removing isolated git worktrees (`.worktrees/issue-NNN`) for issue execution branches. DO NOT USE for managing GitHub PR lifecycles (use `github-issue-pr-lifecycle-agent` instead) or friction logging (use `github-issue-agent` instead).

The `github-issue-worktree-agent` skill manages isolated workspace environments using `git worktree`. It ensures agent work on specific issues takes place in isolated branches under `.worktrees/issue-NNN` without dirtying or interfering with the main working directory.

---

## Quick Start & CLI

- **Helper Script:** `plugins/dev-utils/skills/github-issue-worktree-agent/scripts/issue_worktree_manage.py`

```bash
# Create a worktree for Issue #123:
python3 plugins/dev-utils/skills/github-issue-worktree-agent/scripts/issue_worktree_manage.py create --issue 123 --base main

# List active worktrees:
python3 plugins/dev-utils/skills/github-issue-worktree-agent/scripts/issue_worktree_manage.py list

# Remove a worktree for Issue #123:
python3 plugins/dev-utils/skills/github-issue-worktree-agent/scripts/issue_worktree_manage.py remove --issue 123
```

---

## Progressive Disclosure & References

- **Worktree Management Guide**: [references/worktree-guide.md](references/worktree-guide.md) — safety contracts, configuration options, and Python API interface.
- **Acceptance Criteria**: [references/acceptance-criteria.md](references/acceptance-criteria.md) — verification contracts and test expectations.
- **Fallback Protocol**: [references/fallback-tree.md](references/fallback-tree.md) — failure recovery procedures and dirty worktree resolution.
