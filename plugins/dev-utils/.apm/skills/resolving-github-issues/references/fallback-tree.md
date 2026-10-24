# Procedural Fallback Tree: resolving-github-issues

## `worktree` mode
### 1. Worktree Path Already Exists
- **Condition**: `.worktrees/issue-NNN` directory already present.
- **Action**: Check if registered in `git worktree list`. If stale directory remains, run `git worktree prune` and retry.

### 2. Uncommitted Changes during Removal
- **Condition**: Worktree removal fails due to dirty state.
- **Action**: Prompt user or require `--force` flag before running destructive worktree deletion.

### 3. Git Worktree Not Supported
- **Condition**: Bare git repository or older git version without worktree support.
- **Action**: Fall back to standard git branch switching or report environment limitation.

## `pr-lifecycle` mode
### 1. Missing GitHub CLI (`gh`)
- **Condition**: `gh` executable not found in PATH.
- **Action**: Abort live execution. Output instructions to install GitHub CLI (`brew install gh` or platform package manager) and authenticate via `gh auth login`.

### 2. Dirty Working Directory
- **Condition**: Uncommitted changes present in current working copy.
- **Action**: Refuse to switch or spawn worktrees if working directory state is ambiguous; advise user to stash or commit first.

### 3. Remote Tracking Failure
- **Condition**: Git push fails due to branch conflicts or remote permission errors.
- **Action**: Halt pipeline before PR creation. Do not close the issue prematurely.
