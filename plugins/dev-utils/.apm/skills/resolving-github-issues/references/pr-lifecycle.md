# Issue to worktree to PR to closure (`pr-lifecycle` mode)

Orchestrates the end-to-end issue resolution lifecycle: Issue -> Worktree -> Implementation -> PR Creation -> Resolution Closure.

## Critical Constraints
- **Scope Boundary**: USE ONLY for end-to-end lifecycle orchestration. For standalone worktree isolation, use the `worktree` mode. For issue logging, use the `managing-github-issues` skill (`log` mode).
- **Dry-Run by Default**: Generates pipeline payload in preview mode; requires `--execute` for live branch/PR mutations.
- **Worktree Isolation**: Implementation must occur strictly in `.worktrees/issue-NNN` to keep the primary workspace clean.
- **Verification Gate**: Automated tests must pass prior to opening pull requests.

## Quick start

```bash
# Preview full lifecycle orchestration (dry-run)
python3 scripts/issue_pr_orchestrate.py \
  --issue 42 --title "Fix login bug" --body "Resolves crash on empty password"

# Execute live end-to-end lifecycle
python3 scripts/issue_pr_orchestrate.py \
  --issue 42 --title "Fix login bug" --body "Resolves crash on empty password" \
  --execute
```

## Workflow

1. **Phase 1: Worktree Provisioning**: Create isolated git worktree at `.worktrees/issue-NNN` branching from trunk.
2. **Phase 2: Implementation & Tests**: Apply patch within the isolated worktree and execute the local test suite.
3. **Phase 3: Pull Request Creation**: Push branch to remote and open GitHub PR referencing the issue (`Resolves #NNN`).
4. **Phase 4: Resolution & Cleanup**: Confirm merge, close issue with appropriate labels, and tear down the worktree.

## Verification
