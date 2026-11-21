---
name: running-control-plane
plugin: agent-agentic-os
description: >
  On-demand gated engineering control plane: registers a job in `context/control_plane.db`,
  guides lean 10-state intake/planning/review/worktree/verification/closure with human SSH
  signatures and signed review presets. Use when registering a governed job, checking control-plane
  mode (`enabled` / `on-demand` / `disabled`), running health checks, simulating transitions, or
  managing task worktrees. Not for project setup or key creation (use setting-up-agentic-os) or
  improving skills (use improving-skills-in-lab).
allowed-tools: Bash, Read, Write, Edit
---

# Running the control plane

Gated engineering workflow: a task is registered in `context/control_plane.db`, specified, approved by a human signature, built in a worktree, verified and closed. Each mode below was a separate skill; its full workflow is a reference loaded when that mode starts.

## Contents

- [Critical constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical constraints

1. **Check the mode first.** Run `python3 scripts/control_plane_mode.py status`. In `disabled` mode, skip registration and gating. In `on-demand` mode, unregistered branches pass and only registered jobs are gated (note: `on-demand` is cooperative; `enabled` is the strictly enforcing mode).
2. **Humans sign, agents never.** The three gates (Gate 1 `PLAN_REVIEW -> APPROVED`, Gate 3 `WORKTREE_REVIEW -> VERIFY_EXIT`, `DONE`) and review presets/skips (`signed_decisions`) need a human `ssh-keygen -Y sign`. Never record a decision, approval or review skip on the human's behalf, and never run key enrollment.
3. **Read before acting.** Read the transition guidance and the database first; say which parts were read.
4. **One question per turn**, answered from context and the running directives ledger first. Task artifacts live in `docs/plans/work-tasks/<task-id>/`.
5. **Stop on a blocked gate.** State cause and cost; no workaround commands or direct database edits.
6. **Lifecycle authority & ask before stopping.** Authorized retries and automatic containment/rollback inside the approved plan proceed on their own and save diagnostics (failed diff, logs, transcript path) BEFORE rollback. Any discretionary cancel, restart, retry beyond the plan, scope change, or discarding of output asks the human first; never choose or dispatch reviewers yourself.
7. **Skills are read-only at runtime.** Tests and scripts never write into a skill folder, source or installed; artifacts go to the repository root the control plane resolves, a temp directory or a gitignored folder.

## Quick start

```bash
python3 scripts/control_plane_mode.py status
cd scripts && python3 -m control_plane transition-guidance --task-id <task-id>
```

## Workflow

| Mode | Use when | Run | Workflow |
|---|---|---|---|
| `intake` | Starting or resuming a governed job | `cd scripts && python3 -m control_plane <verb>` | [intake](references/modes/intake.md) |
| `mode` | Switching between `enabled`, `on-demand`, `disabled`, or checking status | `scripts/control_plane_mode.py enable \| on-demand \| disable \| status` | [mode](references/modes/mode.md) |
| `health` | Checking liveness, event bus, locks, memory, os metrics, "system monitor", or whether the signing identity is ready (status check) | `scripts/kernel.py`; signing check: `setup_ciba_identity.py --check` from `setting-up-agentic-os` | [health](references/modes/health.md) |
| `simulator` | Testing a transition, edge or its guidance without real state ("simulate", "dry run", "did I break the edge rules") | `scripts/control_plane/run_transition_simulation.py` | [simulator](references/modes/simulator.md) |
| `worktree` | Choosing or cleaning up a worktree for a task | `scripts/capability_probe.py`, `scripts/worktree_manager.py` | [worktree](references/modes/worktree.md) |

Project setup (`init`) and the human signing key (`signing-setup`) live in the `setting-up-agentic-os` skill, which needs this one installed beside it.

**Routing rule:** the table above only routes. Before acting in a mode, read that mode's workflow file in full (the last column); open the detail references below only from inside it.

## Verification

Run `python3 -m pytest tests` from this skill's folder. Each mode's gates are in [acceptance-criteria.md](references/acceptance-criteria.md); on failure follow [fallback-tree.md](references/fallback-tree.md).

## References

Detail files, grouped by the mode that uses them. Read the mode workflow first.

- **intake**: [adversarial-plan-audit](references/adversarial-plan-audit.md) • [edge-matrix](references/edge-matrix.md) • [healthy-transcript](references/healthy-transcript.md) • [intake-detailed-reference](references/intake-detailed-reference.md) • [multi-round-external-review-protocol](references/multi-round-external-review-protocol.md)
- **health**: [health-detailed-reference](references/health-detailed-reference.md)
- **simulator**: [cheap-agent-transition-simulation](references/cheap-agent-transition-simulation.md)
- **worktree**: [worktree-reconciliation-and-multi-worktree-practices](references/worktree-reconciliation-and-multi-worktree-practices.md)
- **shared**: [acceptance-criteria](references/acceptance-criteria.md) • [agentic-os-skill-map](references/agentic-os-skill-map.md) • [control-plane-architecture](references/control-plane-architecture.md) • [control-plane-rebuild-recovery](references/control-plane-rebuild-recovery.md) • [control-plane-simulation-protocol](references/control-plane-simulation-protocol.md) • [fallback-tree](references/fallback-tree.md) • [implementation-ledger-contract](references/implementation-ledger-contract.md) • [architecture](references/architecture/architecture.md) • [context-folder-patterns](references/architecture/context-folder-patterns.md) • [vision](references/architecture/vision.md)
