# Issue worktrees (`worktree` mode)

Provisions and manages isolated git worktrees (`.worktrees/issue-NNN`) for clean issue execution branches.

## Critical Constraints
- **Scope Boundary**: USE ONLY for worktree lifecycle operations. DO NOT USE for PR lifecycles (use the `pr-lifecycle` mode) or issue logging (use the `managing-github-issues` skill (`log` mode)).
- **Standard Location**: Worktrees must strictly reside within `.worktrees/issue-NNN` relative to repository root.
- **Safe Teardown**: Check `git status` prior to removal; never force-prune uncommitted work without confirmation.
- **Branch Tracking**: Branch naming must consistently map to the issue identifier (`issue-NNN`).

## Quick start

```bash
# Provision isolated worktree for Issue #123
python3 scripts/issue_worktree_manage.py \
  create --issue 123 --base main

# List active worktrees
python3 scripts/issue_worktree_manage.py list

# Clean up worktree after resolution
python3 scripts/issue_worktree_manage.py \
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
python3 scripts/issue_worktree_manage.py list

```
