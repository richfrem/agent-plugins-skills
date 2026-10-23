---
name: resolving-github-issues
plugin: dev-utils
description: >
  Runs issue execution in isolated git worktrees (.worktrees/issue-NNN) and orchestrates
  the issue to worktree to PR to closure flow, dry-run first. Use to create, list or
  remove an issue worktree, or to take an issue through implementation, tests, PR and
  closure. Not for logging, ranking or auditing issues (use managing-github-issues).
allowed-tools: Bash, Read, Write
---

# Resolving GitHub Issues (`resolving-github-issues`)

Workspace and delivery for an issue: isolate it, implement it, ship it, clean up.

## Contents

- [Constraints](#constraints) • [Quick Start](#quick-start) • [Modes](#modes) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

- **Dry-run first**: live branch, push and PR mutations need `--execute`.
- **Isolation**: implementation happens only in `.worktrees/issue-NNN`, on a branch named for the issue.
- **Safe teardown**: check `git status` before removal; never force-prune uncommitted work without confirmation.
- **Test gate**: the test suite passes before a PR is opened.
- **Repository rules win**: follow the project's git rules on branches, PRs and hooks (for example, PRs need an explicit user request).

## Quick Start

```bash
python3 scripts/issue_worktree_manage.py create --issue 123 --base main
python3 scripts/issue_pr_orchestrate.py --issue 42 --title "Fix login bug" --body "Resolves crash on empty password"
```

## Modes

| Mode | Script | Use for | Reference |
|---|---|---|---|
| `worktree` | `issue_worktree_manage.py` (`create`, `list`, `remove`) | Provision and tear down `.worktrees/issue-NNN` | [worktree.md](references/worktree.md) |
| `pr-lifecycle` | `issue_pr_orchestrate.py` | Worktree, implementation, tests, PR, closure | [pr-lifecycle.md](references/pr-lifecycle.md) |

## Workflow

1. Pick the mode and read its reference.
2. Inspect existing worktrees and branch names for collisions (`issue_worktree_manage.py list`).
3. Run the script in dry-run; rerun with `--execute` when authorized.
4. On failure follow [fallback-tree.md](references/fallback-tree.md); on success tear down the worktree.

## Verification

```bash
python3 scripts/issue_worktree_manage.py list
```

Check the mode's section in [acceptance-criteria.md](references/acceptance-criteria.md).

## References

- [worktree.md](references/worktree.md) • [pr-lifecycle.md](references/pr-lifecycle.md) • [worktree-guide.md](references/worktree-guide.md) • [lifecycle-guide.md](references/lifecycle-guide.md)
- [acceptance-criteria.md](references/acceptance-criteria.md) • [fallback-tree.md](references/fallback-tree.md)
