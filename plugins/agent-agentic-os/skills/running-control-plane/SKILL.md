---
name: running-control-plane
plugin: agent-agentic-os
description: >
  CRITICAL INTAKE GATEWAY: use at the start of any non-trivial engineering task, feature, refactor,
  multi-file bugfix, work package or new idea, including requests to explore, brainstorm, build, fix
  or change something, before planning or code changes. Enforces read-only discovery, 1-3 structured
  questions with defaults, control-plane registration and the immutable four-pillar TASK_SPEC.md.
  Also runs the rest of the control plane: health ("run health check", "check os metrics", "system
  monitor", event bus, locks, memory, "is my signing identity ready" status check), transition
  simulation ("dry run transition", "simulate transition", "check edge X -> Y"), worktree selection,
  and gating on/off ("disable the control plane", "turn off the push guard", "stop gating my commits").
  Not for project setup or key creation (use setting-up-agentic-os) or improving skills (use improving-skills-in-lab).
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

1. **Check the mode first.** Run `python3 scripts/control_plane_mode.py status`. When it says `disabled`, say so, skip registration and gating, and offer to enable.
2. **Humans sign, agents never.** The three gates (APPROVED, VERIFY_EXIT, DONE) need a human `ssh-keygen -Y sign`. Never record a decision, approval or review skip on the human's behalf, and never run key enrollment.
3. **Read before acting.** Read the transition guidance and the database first; say which parts were read.
4. **One question per turn**, answered from context and the running directives ledger first. Task artifacts live in `docs/plans/work-tasks/<task-id>/`.
5. **Stop on a blocked gate.** State cause and cost; no workaround commands or direct database edits.

## Quick start

```bash
python3 scripts/control_plane_mode.py status        # is gating on?
python3 scripts/control_plane/coordinator.py transition-guidance --task-id <task-id>
```

## Workflow

| Mode | Use when | Run | Workflow |
|---|---|---|---|
| `intake` | Starting any non-trivial task; resuming one | `scripts/agent_control.py`, `scripts/control_plane/coordinator.py` | [intake](references/modes/intake.md) |
| `mode` | Enabling, disabling or checking gating | `scripts/control_plane_mode.py enable \| disable \| status` | [mode](references/modes/mode.md) |
| `health` | Checking liveness, event bus, locks, memory, os metrics, "system monitor", or whether the signing identity is ready (status check) | `scripts/kernel.py`; signing check: `setup_ciba_identity.py --check` from `setting-up-agentic-os` | [health](references/modes/health.md) |
| `simulator` | Testing a transition, edge or its guidance without real state ("simulate", "dry run", "did I break the edge rules") | `scripts/control_plane/run_transition_simulation.py` | [simulator](references/modes/simulator.md) |
| `worktree` | Choosing or cleaning up a worktree for a task | `scripts/capability_probe.py`, `scripts/worktree_manager.py` | [worktree](references/modes/worktree.md) |

Project setup (`init`) and the human signing key (`signing-setup`) live in the `setting-up-agentic-os` skill, which needs this one installed beside it.

**Routing rule:** the table above only routes. Before acting in a mode, read that mode's workflow file in full (the last column); open the detail references below only from inside it.

## Verification

Run `python3 -m pytest tests` from this skill's folder. Each mode's gates are in [acceptance-criteria.md](references/acceptance-criteria.md); on failure follow [fallback-tree.md](references/fallback-tree.md).

## References

Detail files, grouped by the mode that uses them. Read the mode workflow first.

- **intake**: [edge-matrix](references/edge-matrix.md) • [healthy-transcript](references/healthy-transcript.md) • [intake-detailed-reference](references/intake-detailed-reference.md) • [multi-round-external-review-protocol](references/multi-round-external-review-protocol.md)
- **health**: [health-detailed-reference](references/health-detailed-reference.md)
- **simulator**: [cheap-agent-transition-simulation](references/cheap-agent-transition-simulation.md)
- **worktree**: [worktree-reconciliation-and-multi-worktree-practices](references/worktree-reconciliation-and-multi-worktree-practices.md)
- **shared**: [acceptance-criteria](references/acceptance-criteria.md) • [agentic-os-skill-map](references/agentic-os-skill-map.md) • [control-plane-architecture](references/control-plane-architecture.md) • [control-plane-rebuild-recovery](references/control-plane-rebuild-recovery.md) • [control-plane-simulation-protocol](references/control-plane-simulation-protocol.md) • [fallback-tree](references/fallback-tree.md) • [implementation-ledger-contract](references/implementation-ledger-contract.md) • [architecture](references/architecture/architecture.md) • [context-folder-patterns](references/architecture/context-folder-patterns.md) • [vision](references/architecture/vision.md)
