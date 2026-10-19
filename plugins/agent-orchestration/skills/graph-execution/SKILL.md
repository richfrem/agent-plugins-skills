---
name: graph-execution
plugin: agent-orchestration
description: Executes a compiled graph-manifest.json (from graph-planner) with a deterministic DAG runner - bounded parallel reads, strictly ordered mutations in an isolated git worktree, verifier-hash gates, per-node commits, rollback on failure, and append-only receipts. Use when running, executing, or resuming an existing graph manifest.
allowed-tools: Bash, Read, Write
---

# Graph Execution (`graph-execution`)

Deterministic executor for task graphs compiled by `graph-planner`. Enforces total ordering for mutations, concurrency caps for reads, and automated rollback upon failure.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [State Machine](#state-machine)
- [Workflow](#workflow)
- [Limitations](#limitations)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Workspace Confinement**: Mutations require an isolated git worktree via `--worktree` or `--create-worktree`. `--no-workspace` is permitted only for read-only DAGs and never resets or cleans the checkout.

- **Caller Governance Contract**: Caller environment owns workspace lifecycle and human approval. The runner never pushes, merges, or deletes worktrees.

- **Zero Autonomous Merge**: Merging is strictly caller-managed; the runner stops after recording terminal state.

- **Mutation Boundaries**: Mutations must touch only declared `mutation_targets` and never modify `forbidden_paths`.

- **Human-Bound Manifest SHA**: Under `--approval none`, `--expect-manifest-sha256` must come from a human approval step (for example the control plane's signed Gate 1). Never compute it yourself for a manifest you wrote or edited.

- **Fail Closed**: If `--approval prompt` is selected in a non-interactive shell (including an agent's Bash tool), execution halts immediately before any mutation. Ask the human to run the command in their terminal instead.

## Quick start

```bash
# Execute compiled manifest inside an isolated worktree (human runs this in a terminal)
python3 scripts/graph_runner.py graph-manifest.json --worktree .worktrees/task-001 --approval prompt

# Autonomous run of a human-approved manifest
python3 scripts/graph_runner.py graph-manifest.json --worktree .worktrees/task-001 \
  --approval none --expect-manifest-sha256 <approved-sha256>

# Run read-only graph in current directory
python3 scripts/graph_runner.py read-manifest.json --no-workspace --approval none
```

## State Machine

The runner is a ready-set scheduler, not a fixed phase sequence: each loop it runs every ready `parallel_read` as one bounded batch, otherwise the first ready non-read node.

See [graph_execution_state_machine.mmd](references/diagrams/graph_execution_state_machine.mmd) for the full transition diagram: VALIDATE -> PREFLIGHT -> SCHEDULE -> (READ_BATCH | SINGLE_NODE) -> SCHEDULE ... -> SUCCESS, with FALLBACK and HALT branches.

## Workflow

1. **VALIDATE**: Check manifest SHA (when given), schema, and topology. Mutation or irreversible graphs under `--approval none` need `--expect-manifest-sha256` and a root `verifier_gate` with `role: "approval"`.

2. **PREFLIGHT**: Verify working tree is clean (`git status --porcelain`; skipped for `--no-workspace`). Record starting commit SHA.

3. **READ BATCHES**: Execute ready read-only nodes concurrently up to `max_parallel_concurrency`. After each batch, fail if `git status` or HEAD changed.

4. **SINGLE NODES**: Run ready gates, barriers, and mutations one at a time. Check `verifier_hash` first. Each node is judged by exit code; `output_contract` checks belong in the node's command.

5. **MUTATIONS**: Enforce `mutation_targets` and `forbidden_paths`, then commit once per mutation that changed files. A mutation with no changes succeeds without a commit.

6. **FAILURE**: Retry up to `max_retries_per_node` (mutation debris reset between attempts), then run `fallback_node_id` once its dependencies are complete.

7. **TERMINAL**: Record `success`, `rolled_back` (worktree reset to `<start_sha>` with `git clean -fd`), or `halted` (`--no-workspace`, checkout untouched) in `state.json`.

## Limitations

- `tier` is a planning label; every `command_or_eval` runs with `bash -c`, so model nodes must call a CLI inside the command.
- `input_bindings` and `output_contract` are not enforced by the runner. Nodes pass data through `$GRAPH_SCRATCH_DIR` sibling directories.
- Boundary checks see only what git reports: writes to gitignored paths or outside the repo are not detected or rolled back.

## Verification

```bash
# Inspect append-only execution receipts (anchored in git common dir to survive rollback)
cat "$(git rev-parse --git-common-dir)/graph-run/<graph_id>/<run_id>/receipts.jsonl"

# Audit runner state and exit status
cat "$(git rev-parse --git-common-dir)/graph-run/<graph_id>/<run_id>/state.json"
```

## References

- [graph-manifest-schema.json](references/graph-manifest-schema.json) - Manifest contract the runner validates.
- [topology-rules.md](references/topology-rules.md) - Structural rules the runner enforces.
- [acceptance-criteria.md](references/acceptance-criteria.md) - Startup gates, invariants, and evidence criteria.
- [fallback-tree.md](references/fallback-tree.md) - Runner failure recovery protocols.
- [PATTERN_GUIDE.md](references/PATTERN_GUIDE.md) - Comparative loop patterns.
- [map-debt.md](references/map-debt.md) - Open and resolved friction for agent-orchestration.
