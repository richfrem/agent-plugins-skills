# Acceptance Criteria: resolving-github-issues

## `worktree` mode
### Functional Criteria
1. **Worktree Creation**: `create` creates branch `issue-NNN` and directory `.worktrees/issue-NNN`.
2. **Worktree Listing**: `list` outputs JSON / formatted list of existing issue worktrees.
3. **Safe Cleanup**: `remove` detaches and cleans `.worktrees/issue-NNN` safely, requiring `--force` if uncommitted changes exist.
4. **Idempotence**: Re-requesting creation of an existing worktree fails safely or reports existing status.

### Non-Functional Criteria
1. **Progressive Disclosure**: SKILL.md remains <= 80 lines routing to references.
2. **Isolation**: Never alters workspace files outside `.worktrees/`.

## `pr-lifecycle` mode
### Functional Criteria
1. **Dry-Run Generation**: Running without `--execute` generates a deterministic JSON payload preview without modifying git or GitHub state.
2. **Execution Safety**: Execution requires `--execute` and valid git repository context.
3. **Traceability**: PR body automatically references `Closes #NNN` to ensure issue resolution linkage.
4. **Worktree Lifecycle**: Creates branch/worktree, pushes PR branch, and verifies status cleanly.

### Non-Functional Criteria
1. **Progressive Disclosure**: SKILL.md remains <= 80 lines routing to references.
2. **Zero Uncaught Exceptions**: Handles missing `gh` CLI or failed git commands gracefully with non-zero exit codes.
