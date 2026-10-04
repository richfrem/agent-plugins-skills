---
name: select-loop-strategy
plugin: agent-orchestration
description: Interactive pattern selector that diagnoses task characteristics, compiles a decision record, and hands off to the appropriate pattern planner. Triggers on "which orchestration pattern", "how should I orchestrate", "plan this workflow", "should this be a DAG".
allowed-tools: Read, Write, Bash
---

# Select Loop Strategy (`select-loop-strategy`)

Interactive front door for choosing an execution topology and compiling a structured decision record before planning begins.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Pattern Comparison](#pattern-comparison)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Governance Orthogonal**: Human approvals and worktree confinement wrap all patterns identically. Never ask about approval or rollback (those belong to caller governance).
- **Pattern-Owned Plan Artifacts**: Each pattern produces its own native artifact (`graph` -> `graph-manifest.json`, `dual-loop` -> `task_packet_*.md`, `swarm` -> `*.job.md`).
- **Read-Only DAGs Valid**: Structural fan-out with join barriers and zero mutations qualifies for graph routing.
- **Stand-alone Independence**: Zero dependencies on external plugins or control plane code.

## Quick start

```bash
# Non-interactive evaluation with answers
python3 scripts/select_strategy.py --answers '{"unit_structure":"one_bounded","ordering_convergence":"none","assurance_need":"normal","task_nature":"build_fix"}'

# Interactive pattern selection with task-scoped output
python3 scripts/select_strategy.py --out docs/plans/work-tasks/my-task/
```

## Workflow

1. **Context First**:
   Read caller-supplied brief, spec, plan, or diagnostic files. Derive answers for known dimensions from explicit requirements; ask only about unresolved dimensions.

2. **Diagnostic Interview (Max 4 Questions, 1 per turn)**:
   - **Unit structure**: minimal direct change | one bounded change | distinct steps with dependencies | many identical independent units
   - **Ordering/convergence**: none | results must merge at a barrier | ordered mutations with gates between them
   - **Assurance need**: normal | adversarial review required (security/architecture)
   - **Nature**: build/fix | exploratory research | system/friction optimization
   Each question presents structured options with a recommended default (`Option A [Recommended]`).

3. **Deterministic Selection**:
   Execute `scripts/select_strategy.py` with gathered answers. The script determines the topology based on explicit rules:
   - Many identical independent units -> `agent-swarm`
   - Distinct steps + barrier or ordered mutations -> `graph`
   - One bounded change -> `dual-loop`
   - Minimal direct edit -> `direct`
   - Adversarial assurance -> `red-team-review` (wrapper modifier)
   - Exploratory research -> `learning-loop`
   - System optimization -> `triple-loop-learning`

4. **Confirm & Record Decision**:
   Write `select-loop-strategy-decision.json` (and `.md`) to the task directory (via `--out docs/plans/work-tasks/<task-id>/`). Present the decision to the human to confirm or override. Record any requested override in the decision artifact.

5. **Hand Off**:
   Name the next skill to invoke with its input path (e.g. `graph-planner --decision docs/plans/work-tasks/<task-id>/select-loop-strategy-decision.json`). Do not invoke downstream execution automatically.

## Pattern Comparison

| Pattern | Planner / Dispatcher | Executor | Plan Artifact | Primary Use Case |
|---|---|---|---|---|
| **Graph** | `graph-planner` | `graph-execution` | `graph-manifest.json` | Fan-out reads, sync barriers, ordered mutations |
| **Dual-Loop** | `agent_orchestrator.py packet` | `dual-loop` | `handoffs/task_packet_*.md` | Bounded bug fixes, localized feature coding |
| **Swarm** | `swarm_run.py --dry-run` | `agent-swarm` | `*.job.md` | Batch conversions, mass refactors across files |
| **Adversarial** | `red-team-review` | `red-team-review` | Review brief | Security audits, architecture stress-testing |
| **Solo** | `learning-loop` | `learning-loop` | Research brief | Single-stream open-ended discovery |
| **Meta** | `triple-loop-learning` | `triple-loop-learning` | Friction log | Autonomous system optimization |

## Verification

```bash
# Run strategy selection tests
pytest plugins/agent-orchestration/tests/test_select_strategy.py -v
```

## References

- [PATTERN_GUIDE.md](references/PATTERN_GUIDE.md) - Comparative loop patterns.
- [acceptance-criteria.md](references/acceptance-criteria.md) - Verification criteria and contracts.
- [fallback-tree.md](references/fallback-tree.md) - Escalation paths for ambiguous routing.
