---
name: worktree-manager
plugin: agent-agentic-os
description: >
  Selects confirmed native worktree facilities or the governed portable
  repository worktree fallback, validates placement, and reports cleanup guidance.
allowed-tools: Bash, Read
---

# Worktree Manager

Use this skill when a task needs an isolated worktree or when the active runtime
may provide native worktree management.

1. Probe the active runtime with `scripts/capability_probe.py`.
2. Treat the returned capability result as authoritative. Never infer native
   worktree support from a model name or an installed binary.
3. If `native_worktree` is true, follow the returned activation guidance and
   retain the task's control-plane gates.
4. Otherwise use the portable plan from `scripts/worktree_manager.py` and
   delegate lifecycle operations to the `issue-worktree-agent` skill; its path
   must remain below `<repo>/.worktrees/<task-id>`.
5. Before creating any worktree, `git fetch origin main` and base the new
   branch on `origin/main` — never on local `main`, which may be stale or
   hold uncommitted state. A worktree only ever contains committed content;
   see `references/worktree-reconciliation-and-multi-worktree-practices.md`
   for why and for the full reconciliation and multi-worktree contract.
6. Report the selected strategy, exact path, branch, activation guidance, and
   cleanup command before mutating the repository.

Native and portable execution have the same approval, verification, and review
requirements. Native execution is an implementation facility, not a governance
bypass.

## Dirty pre-worktree state and concurrent worktrees

Do not rely on agent self-report that pre-worktree changes on the source checkout were carried
into the worktree, or that a concurrent worktree's merged work is still intact after a rebase —
both are enforced or documented, not assumed:

- **Pre-worktree dirty state**: the `APPROVED -> IN_WORKTREE` transition runs a deterministic,
  code-executed reconciliation check (`main_worktree_reconciliation`) that force-copies dirty
  source-checkout files into the worktree and hard-blocks on any genuine conflict. See
  `references/worktree-reconciliation-and-multi-worktree-practices.md` §1.
- **Concurrent worktrees**: rebase onto fresh `origin/main` immediately before merging any
  worktree branch — never assume the branch's original base commit is still current, especially
  given this repository's squash-merge convention. See
  `references/worktree-reconciliation-and-multi-worktree-practices.md` §3 for the full
  multi-worktree contract (fresh-base branching, task-scoped file ownership, staging/integration
  branch for overlapping work, mandatory diff review before merge).
