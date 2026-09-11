# Procedural Fallback Tree: GitHub Issue PR Lifecycle

## 1. Missing GitHub CLI (`gh`)
- **Condition**: `gh` executable not found in PATH.
- **Action**: Abort live execution. Output instructions to install GitHub CLI (`brew install gh` or platform package manager) and authenticate via `gh auth login`.

## 2. Dirty Working Directory
- **Condition**: Uncommitted changes present in current working copy.
- **Action**: Refuse to switch or spawn worktrees if working directory state is ambiguous; advise user to stash or commit first.

## 3. Remote Tracking Failure
- **Condition**: Git push fails due to branch conflicts or remote permission errors.
- **Action**: Halt pipeline before PR creation. Do not close the issue prematurely.
