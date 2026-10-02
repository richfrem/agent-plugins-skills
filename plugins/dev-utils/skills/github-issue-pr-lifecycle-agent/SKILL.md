---
name: github-issue-pr-lifecycle-agent
plugin: dev-utils
description: >
  Skill for orchestrating the end-to-end GitHub issue lifecycle flow: Issue -> Worktree -> Implementation -> PR Creation -> Resolution Closure.
  USE ONLY when running or dry-running full lifecycle orchestration for resolving an issue with a PR.
  DO NOT USE for isolated worktree management only (use `github-issue-worktree-agent`) or logging issues (use `github-issue-agent`).
allowed_tools:
  - run_command
  - view_file
  - write_to_file
  - replace_file_content
  - multi_replace_file_content
  - grep_search
  - list_dir
---

# GitHub Issue PR Lifecycle Agent (github-issue-pr-lifecycle-agent)

Orchestrates the end-to-end issue resolution lifecycle: Issue -> Worktree -> Implementation -> PR Creation -> Resolution Closure.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Scope Boundary**: USE ONLY for end-to-end lifecycle orchestration. For standalone worktree isolation, use `github-issue-worktree-agent`. For issue logging, use `github-issue-agent`.
- **Dry-Run by Default**: Generates pipeline payload in preview mode; requires `--execute` for live branch/PR mutations.
- **Worktree Isolation**: Implementation must occur strictly in `.worktrees/issue-NNN` to keep the primary workspace clean.
- **Verification Gate**: Automated tests must pass prior to opening pull requests.

## Quick start

```bash
# Preview full lifecycle orchestration (dry-run)
python3 plugins/dev-utils/skills/github-issue-pr-lifecycle-agent/scripts/issue_pr_orchestrate.py \
  --issue 42 --title "Fix login bug" --body "Resolves crash on empty password"

# Execute live end-to-end lifecycle
python3 plugins/dev-utils/skills/github-issue-pr-lifecycle-agent/scripts/issue_pr_orchestrate.py \
  --issue 42 --title "Fix login bug" --body "Resolves crash on empty password" \
  --execute
```

## Workflow

1. **Phase 1: Worktree Provisioning**: Create isolated git worktree at `.worktrees/issue-NNN` branching from trunk.
2. **Phase 2: Implementation & Tests**: Apply patch within the isolated worktree and execute the local test suite.
3. **Phase 3: Pull Request Creation**: Push branch to remote and open GitHub PR referencing the issue (`Resolves #NNN`).
4. **Phase 4: Resolution & Cleanup**: Confirm merge, close issue with appropriate labels, and tear down the worktree.

## Verification

```bash
# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/dev-utils/skills/github-issue-pr-lifecycle-agent --mode source
```

## References
- [lifecycle-guide.md](references/lifecycle-guide.md) - Pipeline sequencing, safety contracts, and API options.
- [acceptance-criteria.md](references/acceptance-criteria.md) - Verification contracts and test criteria.
- [fallback-tree.md](references/fallback-tree.md) - Failure recovery and manual recovery procedures.
