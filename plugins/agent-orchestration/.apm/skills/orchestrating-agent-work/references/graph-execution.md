# Graph execution (deterministic DAG runner)

Deterministic executor for task graphs compiled by graph planning ([graph-planning.md](graph-planning.md)). Enforces total ordering for mutations, concurrency caps for reads, and automated rollback upon failure.

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

See [graph_execution_state_machine.mmd](diagrams/graph_execution_state_machine.mmd) for the full transition diagram: VALIDATE -> PREFLIGHT -> SCHEDULE -> (READ_BATCH | SINGLE_NODE) -> SCHEDULE ... -> SUCCESS, with FALLBACK and HALT branches.

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

## Observing a run

The runner is a separate program: it launches each node (`bash -c`, model nodes through a CLI such as `claude -p`) as its own process. Claude Code does not know about those processes, so `/tasks` and `/agents` do not list them. The supervisor (the agent that started the run) must therefore say, when it starts a run, how the human can watch it. Do these:

1. Start the runner as a tracked background task (`run_in_background`), never with `nohup &`, so the run itself shows in `/tasks`.
2. Give the human these commands (replace `<graph_id>` and `<run_id>`):
   - which nodes finished: `cut -c1-100 "$(git rev-parse --git-common-dir)/graph-run/<graph_id>/<run_id>/receipts.jsonl"`
   - status and failed nodes: `cat "$(git rev-parse --git-common-dir)/graph-run/<graph_id>/<run_id>/state.json"`
   - running worker processes: `ps -eo pid,etime,command | grep "claude -p" | grep -v grep | cut -c1-120`
   - a worker's actions: tail the newest `*.jsonl` under `~/.claude/projects/<worktree path with / replaced by ->/`.
3. Report each finished node and each failure to the human as it happens; do not wait for the end.

Parallel fan-out appears as several `parallel_read` nodes started in one batch (`[PARALLEL BATCH] Running N parallel read node(s)` in the log, up to `max_parallel_concurrency`). Mutations never overlap.

## What the runner enforces and what it only instructs

Enforced by code: manifest SHA binding, schema and topology validation, `verifier_hash` of the first file named in a command, clean tree and unchanged HEAD after read batches, `mutation_targets` and `forbidden_paths` as git reports them, ordered mutations, one commit per mutation, rollback to the start commit on failure.

Only instructed (the worker prompt, not the runner): which tools a model node may use, never running `git`, never writing outside the worktree. Writes to gitignored paths or outside the repository are invisible to the runner. A worker given `python -m pytest` can run arbitrary Python. Treat the human code review as the control for those limits, and give workers the narrowest tool list that works.

A failed mutation node rolls back the whole worktree, including a worker run that succeeded but whose commit was rejected (for example by a pre-commit hook). Before starting a run, check which commit hooks apply to the files the slices will change, and make each slice satisfy them in its own commit.

## Verification

```bash
# Inspect append-only execution receipts (anchored in git common dir to survive rollback)
cat "$(git rev-parse --git-common-dir)/graph-run/<graph_id>/<run_id>/receipts.jsonl"

# Audit runner state and exit status
cat "$(git rev-parse --git-common-dir)/graph-run/<graph_id>/<run_id>/state.json"
```
