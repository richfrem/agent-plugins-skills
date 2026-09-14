# Procedural Fallback Tree: GitHub Issue Worktree

## 1. Worktree Path Already Exists
- **Condition**: `.worktrees/issue-NNN` directory already present.
- **Action**: Check if registered in `git worktree list`. If stale directory remains, run `git worktree prune` and retry.

## 2. Uncommitted Changes during Removal
- **Condition**: Worktree removal fails due to dirty state.
- **Action**: Prompt user or require `--force` flag before running destructive worktree deletion.

## 3. Git Worktree Not Supported
- **Condition**: Bare git repository or older git version without worktree support.
- **Action**: Fall back to standard git branch switching or report environment limitation.
