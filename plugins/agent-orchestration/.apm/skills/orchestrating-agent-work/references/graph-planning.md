# Graph planning (compile and validate a DAG manifest)

Architects, topologically validates, and compiles token-budgeted execution graphs (DAGs) into `graph-manifest.json`.

## Principles

1. **Keep orchestration proportionate to the work.** Use the smallest graph that does the job. The effort of building and running the graph (nodes, pinned scripts, gates, retries) must be less than the effort it saves. Write one line of overhead versus gain in `caller.planning_notes`. If overhead wins, simplify.
2. **Parallelize what is independent.** Independent reads always fan out: scouts, reviewer lenses, baselines. Independent edits go in separate worktrees only when the time saved clearly beats setup plus merge cost. Parallelism is a tool for efficiency, not a goal in itself.
3. **A serial chain is not a graph.** If the work is ordered edits with no fan-out and no join barrier, use `direct`, or a supervised loop with one worker per step and a test run after each ([strategy-dual-loop.md](strategy-dual-loop.md)).
4. **Gates are proportionate.** Run cheap deterministic checks first. Put one independent review on a risky step. Checks a human will review at the end are not per-node gates.
5. **Every gate must be passable by the step before it.** A gate may not depend on work that a later node does.

Smells that mean the graph is too big: N sequential mutations each with their own gate; pinning every helper script; model reviews after trivial edits; more orchestration files than changed files.

## Constraints

- **Ingest Before Interview**: Read caller briefs or task specifications first; ask user questions only on unresolved topological gaps.

- **Zero Parallel Mutations**: Side-effecting mutations must always form a strict linear chain.

- **Read-Only DAGs Valid**: Graphs with zero mutations (pure parallel reads and join barriers) are valid for spikes and discovery.

- **Deterministic Gates**: Use `verifier_gate` with `tier: "deterministic_script"` before expensive model calls.

- **Executable Commands**: graph execution ([graph-execution.md](graph-execution.md)) runs every `command_or_eval` with `bash -c`. Model-tier nodes must call a CLI inside the command and write output to `$GRAPH_SCRATCH_DIR`; never put a bare prompt in `command_or_eval`.

- **Gate Irreversible Actions**: Nodes with external side effects set `reversible: false` and depend on the approval gate.

## Quick start

```bash
# Validate compiled manifest against schema and acyclicity rules
python3 scripts/validate_manifest.py graph-manifest.json
# Add --check-approval-none when running autonomously with --approval none (requires a root verifier_gate with role="approval")
python3 scripts/validate_manifest.py graph-manifest.json --check-approval-none
```

## Workflow

1. **Ingest & Gap Analysis**: Read any existing task briefs, specifications, or `--decision <path>` artifact. When `--decision <path>` is present, skip all pattern-level questions and immediately focus the interview on nodes, barriers, verifiers, and mutations.

2. **Topological Interview**: Interview user only on unresolved gaps (fan-out opportunities, join barriers, verifier scripts, failure escalation).

3. **Enforce Topology Rules**:
   - Fan-out only stateless, read-only tasks.
   - Total ordering on all `sequential_mutation` nodes.
   - Converge parallel branches at a `sync_barrier` whose command checks the workers' output contracts.
   - Allocate `fast_engine` for leaf nodes and `frontier_engine` for synthesis.
   - Give each fallback the same `type` as its primary and, for mutations, the same preceding mutations.

4. **Compile Manifest**: Author `graph-manifest.json` adhering to `graph-manifest-schema.json`. For autonomous `--approval none` mutation graphs, include a leading root `verifier_gate` with `role: "approval"` that every mutation depends on. If you embed a `plan_audit.py check` node in the DAG, mark it `role: "audit"` (every mutation node must depend on it). Write a Mermaid diagram of the DAG next to the manifest (or in the task plan) and show it to the caller.

5. **Validate & Handoff**: Run `validate_manifest.py` (add `--check-approval-none` when the graph will run with `--approval none`). Hand off the manifest path, its SHA256 (`shasum -a 256 graph-manifest.json`), the intended `--approval` mode, and the workspace flag. The human approves that SHA; any later manifest edit requires re-approval.

## Partition analysis (choosing the shape of the graph)

The planner chooses how much of the graph runs in parallel. Decide it from the work, not by habit:

1. List the candidate slices with, for each, the files or folders it edits and what it must read.
2. Mark two slices **independent** only if their edit areas are disjoint and neither needs the other's output. Independent mutation slices still run one after another inside one worktree. Run them in separate worktrees (one graph each, merged by the caller) only when the saved time exceeds the merge cost.
3. Fan out **reads** wherever they are independent: one scout per area before a slice, several reviewer lenses side by side after it (architecture, security, test contract), parallel baselines when their commands do not write to the repository.
4. Set `max_parallel_concurrency` to the widest fan-out, no higher, and keep model cost and the human's rate limits in mind.
5. Record the shape and the reasons in the manifest under `caller.planning_notes` (which slices were parallelised or chained, and why; worker count; worktree choice).

Never put test suites that write into the repository in parallel read nodes: a read node that dirties the shared worktree fails its siblings' immutability check.

## Verification

```bash
# Deterministic manifest validation
python3 scripts/validate_manifest.py graph-manifest.json

# Additionally required for manifests that will run with --approval none
python3 scripts/validate_manifest.py graph-manifest.json --check-approval-none
```
