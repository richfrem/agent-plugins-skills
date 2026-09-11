# Acceptance Criteria: GitHub Issue PR Lifecycle Agent

## Functional Criteria
1. **Dry-Run Generation**: Running without `--execute` generates a deterministic JSON payload preview without modifying git or GitHub state.
2. **Execution Safety**: Execution requires `--execute` and valid git repository context.
3. **Traceability**: PR body automatically references `Closes #NNN` to ensure issue resolution linkage.
4. **Worktree Lifecycle**: Creates branch/worktree, pushes PR branch, and verifies status cleanly.

## Non-Functional Criteria
1. **Progressive Disclosure**: SKILL.md remains <= 80 lines routing to references.
2. **Zero Uncaught Exceptions**: Handles missing `gh` CLI or failed git commands gracefully with non-zero exit codes.
