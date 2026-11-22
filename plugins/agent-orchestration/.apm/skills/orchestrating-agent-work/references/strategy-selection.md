# Strategy selection (diagnostic interview + deterministic selector)

Interactive front door for choosing an execution topology and compiling a structured decision record before planning begins.

## Principles

Choose the lightest strategy that fits. Orchestration effort (nodes, pinned scripts, gates) must stay below the effort it saves; a serial chain is not a graph; parallelize only what is independent and only when the saving beats setup and merge cost. The full list is in [graph-planning.md](graph-planning.md#principles).

## Constraints

- **Governance Orthogonal**: Human approvals and worktree confinement wrap all patterns identically. Never ask about approval or rollback (those belong to caller governance).
- **Pattern-Owned Plan Artifacts**: Each pattern produces its own native artifact (`graph` -> `graph-manifest.json`, `dual-loop` -> `task_packet_*.md`, `swarm` -> `*.job.md`).
- **Read-Only DAGs Valid**: Structural fan-out with join barriers and zero mutations qualifies for graph routing.
- **Stand-alone Independence**: Zero dependencies on external plugins or control plane code.

## Quick start

```bash
# Non-interactive evaluation with answers
python3 scripts/select_strategy.py --answers '{"unit_structure":"one_bounded","ordering_convergence":"none","assurance_need":"normal"}'

# Interactive pattern selection with task-scoped output
python3 scripts/select_strategy.py --out docs/plans/work-tasks/my-task/
```

## Workflow

1. **Context First**:
   Read caller-supplied brief, spec, plan, or diagnostic files. Derive answers for known dimensions from explicit requirements; ask only about unresolved dimensions.

2. **Diagnostic Interview (Max 3 Questions, 1 per turn)**:
   - **Unit structure (`unit_structure`)**: `minimal_direct` (minimal direct change) | `one_bounded` (one bounded change) | `distinct_steps` (distinct steps with dependencies) | `many_identical` (many identical independent units)
   - **Ordering/convergence (`ordering_convergence`)**: `none` | `barrier` (results must merge at a barrier) | `ordered_mutations` (ordered mutations with gates between them)
   - **Assurance need (`assurance_need`)**: `normal` | `adversarial` (adversarial review required: security/architecture)
   Each question presents structured options with a recommended default (`Option A [Recommended]`).

3. **Deterministic Selection**:
   Execute `scripts/select_strategy.py` with gathered answers. The script determines the topology based on explicit rules:
   - Many identical independent units -> `agent-swarm`
   - Distinct steps with two or more independent branches, a join barrier, or an irreversible step that needs an approval gate -> `graph`
   - Ordered mutations alone (a serial chain with no fan-out and no barrier) -> `dual-loop` (or `direct` for a small change); a graph would cost more orchestration than it saves
   - One bounded change -> `dual-loop`
   - Minimal direct edit -> `direct`
   - Adversarial assurance -> `red-team-review` (wrapper modifier; [strategy-red-team-review.md](strategy-red-team-review.md))
   Open-ended research and self-improvement are out of scope here; use agent-agentic-os (`improving-skills-in-lab`).

4. **Confirm & Record Decision**:
   Write `select-loop-strategy-decision.json` (and `.md`) to the task directory (via `--out docs/plans/work-tasks/<task-id>/`). Present the decision to the human to confirm or override. Record any requested override in the decision artifact.

5. **Hand Off**:
   Name the next step (`next_step` in the result, a reference in this skill) with its input path (e.g. [graph-planning.md](graph-planning.md) with `--decision docs/plans/work-tasks/<task-id>/select-loop-strategy-decision.json`). Do not invoke downstream execution automatically.

## Pattern Comparison

| Pattern | Planner / Dispatcher | Executor | Plan Artifact | Primary Use Case |
|---|---|---|---|---|
| **Graph** | graph planning ([graph-planning.md](graph-planning.md)) | graph execution ([graph-execution.md](graph-execution.md)) | `graph-manifest.json` | Fan-out reads, sync barriers, ordered mutations |
| **Dual-Loop** | `agent_orchestrator.py packet` | [strategy-dual-loop.md](strategy-dual-loop.md) | `handoffs/task_packet_*.md` | Bounded bug fixes, localized feature coding |
| **Swarm** | `swarm_run.py --dry-run` | [strategy-agent-swarm.md](strategy-agent-swarm.md) | `*.job.md` | Batch conversions, mass refactors across files |
| **Adversarial** | [strategy-red-team-review.md](strategy-red-team-review.md) | cli-agent persona dispatch | Review brief | Security audits, architecture stress-testing |
| **Async Bot Handoff** | [bot-delegation-patterns.md](bot-delegation-patterns.md) | Asynchronous Cloud/Web VM | Task brief / PR / Webhook | GUI computer-use, telephony, SaaS triage, multimodal research |

## Verification

```bash
# Run strategy selection tests
pytest tests/test_select_strategy.py -v
```
