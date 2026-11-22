# End-to-End Generative Graph Planning & Execution Simulation

A live, cold-read end-to-end simulation of the `orchestrating-agent-work` graph pipeline where a fresh subagent reads `SKILL.md`, `references/graph-planning.md`, and `references/graph-manifest-schema.json` cold, plans and validates a real multi-node `graph-manifest.json`, runs `plan_audit.py`, and executes the graph through `graph_runner.py` (with `--control-plane-task`, `--status`, and `--progress-file`) in an isolated `/private/tmp` sandbox while logging every schema, CLI, and documentation friction point.

## Contents

- [Why This Protocol Exists](#why-this-protocol-exists)
- [Sandbox Setup](#sandbox-setup)
- [Simulation Stages](#simulation-stages)
- [Friction Log & Fix-Verify Loop](#friction-log--fix-verify-loop)

## Why This Protocol Exists

Deterministic unit tests verify individual validators and runner hooks, but only a cold-read generative agent reveals whether the skill's docs, schema, and CLI flags actually guide an orchestrator to:

1. Select `graph` via `select_strategy.py` when parallel read fan-out + ordered mutation is warranted.
2. Author a schema-valid `graph-manifest.json` (including `label`, `control_plane`, and `audit` role dependency invariants) that passes `validate_manifest.py` on the first try.
3. Run the adversarial plan-audit ledger (`plan_audit.py packet -> record -> settle -> check`) cleanly.
4. Execute the manifest via `graph_runner.py` with Gate 1 re-verification (`--control-plane-task`), live observability (`--status`, `--progress-file`), and pre-rollback diff preservation (`failed-diff.patch`).

## Sandbox Setup

1. Create an isolated directory under the OS's **resolved** temp path (on macOS, `/private/tmp/sim-generative-graph-<run>/`).
2. Copy `orchestrating-agent-work` and `running-control-plane` side-by-side into `<sandbox>/skills/`.
3. Initialize a clean git repository at `<sandbox>/repo` with a small Python module and passing unit test, committed on `main`.
4. Initialize `<sandbox>/repo/context/simulation/simulation_control_plane.db` (schema v15) with a task in `PLAN_REVIEW` (or walk `INTAKE -> PLAN_REVIEW`) and `SimulationSigner(<sandbox>/repo/context/simulation/identity)` for the parent agent acting as Human Operator.
5. Never touch the real repository's `context/control_plane.db` or human SSH keys.

## Simulation Stages

1. **Strategy Selection**: Subagent runs `select_strategy.py` for a multi-step task with parallel read/audit fan-out + sequential implementation + verification, confirming `pattern: graph`.
2. **Manifest Authoring & Validation**: Subagent authors `docs/plans/work-tasks/<task-id>/<task-id>-graph-manifest.json` (2 parallel read/audit nodes -> 1 implement node -> 1 verify node, using lightweight deterministic shell/command or local mock executors so no external API cost is incurred) and validates it with `validate_manifest.py`.
3. **Adversarial Plan Audit**: Subagent runs `plan_audit.py packet`, records 2 clean rounds (`plan_audit.py record`), settles (`plan_audit.py settle`), and verifies (`plan_audit.py check`).
4. **Gate 1 Binding (Parent as Human Operator)**: Parent signs `PLAN_REVIEW -> APPROVED` with `SimulationSigner`, binding the manifest SHA-256 and `verdict.json` into the Gate 1 snapshot.
5. **Graph Execution & Observability**: Subagent runs `graph_runner.py` with `--worktree`, `--control-plane-task <task-id>`, `--progress-file`, and checks `--status`, verifying atomic `state.json` `active_nodes` and clean exit.
6. **Pre-Rollback Diff Check (Optional)**: Run a deliberate failing mutation node to verify `failed-diff.patch` is saved before worktree rollback.

## Friction Log & Fix-Verify Loop

1. **Run 1**: Complete stages 1–5 without editing any skill files mid-run. Report all friction findings to the human operator first.
2. **Fix**: Apply surgical fixes to `SKILL.md`, `references/graph-planning.md`, `graph-manifest-schema.json`, `validate_manifest.py`, `plan_audit.py`, or `graph_runner.py`.
3. **Run 2**: Re-run in a fresh `/private/tmp` sandbox with a fresh cold subagent to confirm friction drops to zero.
