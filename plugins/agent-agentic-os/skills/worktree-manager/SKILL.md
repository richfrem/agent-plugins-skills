---
name: worktree-manager
plugin: agent-agentic-os
description: >
  Selects confirmed native worktree facilities or the governed portable
  repository worktree fallback, validates placement, and reports cleanup guidance.
allowed-tools: Bash, Read
---

# Worktree Manager

Selects confirmed native worktree facilities or the governed portable repository worktree fallback, validates placement, and reports cleanup guidance.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Origin Base Invariant**: Before creating any worktree, run `git fetch origin main` and base new branches on `origin/main` — never on local `main`.
2. **Path Confinement**: Portable worktrees must reside strictly below `<repo>/.worktrees/<task-id>`.
3. **Governance Equivalence**: Native worktree execution is an implementation facility, not a governance bypass. Both native and portable execution require identical approval, verification, and review gates.
4. **Reconciliation & Concurrency**: Never assume pre-worktree dirty state or concurrent branches carry over automatically. `APPROVED -> IN_WORKTREE` requires deterministic reconciliation (`main_worktree_reconciliation`). Rebase onto fresh `origin/main` immediately before merging.

## Quick start

Probe the active runtime to determine available worktree facilities:

```bash
python3 scripts/capability_probe.py
```

## Workflow

1. **Probe Runtime**: Run `capability_probe.py` and treat returned capability as authoritative. Never infer native support from model name or binary presence.
2. **Select Facility**:
   - If `native_worktree` is true: follow returned activation guidance and retain task control-plane gates.
   - If portable fallback: generate execution plan via `scripts/worktree_manager.py` and delegate lifecycle management to `issue-worktree-agent`.
3. **Reconcile Base & State**: Fetch `origin/main` and verify base commit. If migrating uncommitted edits, run deterministic reconciliation.
4. **Report & Activate**: Report selected strategy, exact path, branch, activation guidance, and cleanup commands before mutating repository.

## Verification

1. Confirm worktree directory path matches `<repo>/.worktrees/<task-id>`.
2. Verify branch HEAD is derived directly from `origin/main`.
3. Inspect `git status` inside worktree to confirm reconciliation succeeded without uncommitted file collisions.

## References

- [worktree-reconciliation-and-multi-worktree-practices.md](references/worktree-reconciliation-and-multi-worktree-practices.md) — Read when handling dirty working trees, rebase conflicts, or concurrent worktrees.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance gates and readiness checks.
- [fallback-tree.md](references/fallback-tree.md) — Recovery procedures when worktree creation fails.
