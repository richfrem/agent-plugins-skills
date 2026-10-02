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

# GitHub Issue Worktree Agent (github-issue-worktree-agent)

Provisions and manages isolated git worktrees (`.worktrees/issue-NNN`) for clean issue execution branches.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Scope Boundary**: USE ONLY for worktree lifecycle operations. DO NOT USE for PR lifecycles (use `github-issue-pr-lifecycle-agent`) or issue logging (use `github-issue-agent`).
- **Standard Location**: Worktrees must strictly reside within `.worktrees/issue-NNN` relative to repository root.
- **Safe Teardown**: Check `git status` prior to removal; never force-prune uncommitted work without confirmation.
- **Branch Tracking**: Branch naming must consistently map to the issue identifier (`issue-NNN`).

## Quick start

```bash
# Provision isolated worktree for Issue #123
python3 plugins/dev-utils/skills/github-issue-worktree-agent/scripts/issue_worktree_manage.py \
  create --issue 123 --base main

# List active worktrees
python3 plugins/dev-utils/skills/github-issue-worktree-agent/scripts/issue_worktree_manage.py list

# Clean up worktree after resolution
python3 plugins/dev-utils/skills/github-issue-worktree-agent/scripts/issue_worktree_manage.py \
  remove --issue 123
```

## Workflow

1. **Phase 1: Workspace Inspection**: Check for existing worktree directories or branch name collisions.
2. **Phase 2: Worktree Provisioning**: Spawn isolated worktree at `.worktrees/issue-NNN` tracking trunk.
3. **Phase 3: Implementation Context**: Guide agent execution to occur within the isolated worktree directory.
4. **Phase 4: Teardown & Pruning**: Confirm committed state, prune worktree directory, and clean local branch.

## Verification

```bash
# Verify active worktree state
python3 plugins/dev-utils/skills/github-issue-worktree-agent/scripts/issue_worktree_manage.py list

# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/dev-utils/skills/github-issue-worktree-agent --mode source
```

## References
- [worktree-guide.md](references/worktree-guide.md) - Worktree isolation safety contracts and CLI guide.
- [acceptance-criteria.md](references/acceptance-criteria.md) - Verification contracts and test criteria.
- [fallback-tree.md](references/fallback-tree.md) - Failure recovery and dirty worktree resolution.
