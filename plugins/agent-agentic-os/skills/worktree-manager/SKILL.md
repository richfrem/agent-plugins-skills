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
5. Report the selected strategy, exact path, branch, activation guidance, and
   cleanup command before mutating the repository.

Native and portable execution have the same approval, verification, and review
requirements. Native execution is an implementation facility, not a governance
bypass.
