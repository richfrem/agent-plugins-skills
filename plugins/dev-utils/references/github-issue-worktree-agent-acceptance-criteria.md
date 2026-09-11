# Acceptance Criteria: GitHub Issue Worktree Agent

## Functional Criteria
1. **Worktree Creation**: `create` creates branch `issue-NNN` and directory `.worktrees/issue-NNN`.
2. **Worktree Listing**: `list` outputs JSON / formatted list of existing issue worktrees.
3. **Safe Cleanup**: `remove` detaches and cleans `.worktrees/issue-NNN` safely, requiring `--force` if uncommitted changes exist.
4. **Idempotence**: Re-requesting creation of an existing worktree fails safely or reports existing status.

## Non-Functional Criteria
1. **Progressive Disclosure**: SKILL.md remains <= 80 lines routing to references.
2. **Isolation**: Never alters workspace files outside `.worktrees/`.
