# Graph Planning Topology and Token Economic Rules

Normative rules and heuristic validation checks for Directed Acyclic Graphs compiled by `graph-planner`.

## 1. Structural Laws

1. **Rule of Fan-Out (Parallel Scatter)**:
   - Only parallelize pure, stateless, read-only tasks that share the same parent context.
   - Nodes of type `parallel_read` must never invoke state-mutating commands or write to disk within the repository worktree.
   - Scratch writes must be confined strictly to `$GRAPH_SCRATCH_DIR`, which the runner sets to `<git-common-dir>/graph-run/<graph_id>/<run_id>/scratch/<node_id>/`.
   - Before each parallel batch, the runner calculates the SHA256 hash of `git status --porcelain` and records HEAD. When the batch drains, both are recomputed; if either changed, the run fails immediately. This check runs after every batch, independent of any `sync_barrier` node.

2. **Rule of Mutation Total Ordering**:
   - Mutations must never run in parallel, and no `parallel_read` may ever run concurrently with any mutation.
   - All mutations must form a strict, total ordering: each `sequential_mutation` node must depend directly on the preceding mutation node in sequence.
   - If a graph contains mutations, it must execute inside an isolated worktree. Running with `--no-workspace` is strictly rejected for graphs containing mutations.
   - A mutation that leaves the tree unchanged succeeds without a commit (idempotent re-runs are valid).

3. **Rule of Read-Only DAGs**:
   - Read-only DAGs consisting solely of `parallel_read`, `verifier_gate`, and `sync_barrier` nodes (with zero `sequential_mutation` nodes) are fully valid topologies.
   - Read-only graphs are commonly used for research discovery, architecture scans, and multi-source diagnostic spikes.
   - Read-only DAGs may safely run in the current working directory (`--no-workspace`) and with `--approval none`.
   - Under `--no-workspace` the runner never runs `git reset` or `git clean`: on failure it halts and lists changed paths, so the caller's uncommitted work is preserved. A dirty tree is allowed in this mode.

4. **Rule of Leading Approval Gate**:
   - For any graph containing `sequential_mutation` or `reversible: false` nodes, running under autonomous execution (`--approval none`) is permitted only if a root node is a `verifier_gate` with `"role": "approval"`, every mutation and irreversible node depends on it, and the caller passes `--expect-manifest-sha256`.
   - The manifest SHA must come from a human approval step (for example the control plane's signed Gate 1). An agent computing the SHA of a manifest it wrote is not approval.
   - When running with `--approval prompt`, the runner prompts the human operator once before the first mutation node executes, plus once per node marked `"reversible": false`.

5. **Rule of Join Barriers (Fan-In)**:
   - Any fan-out must converge at a typed barrier node before downstream steps can consume the data.
   - A `sync_barrier` node runs only after all of its upstream workers completed successfully. Its `command_or_eval` is where output contracts are checked (for example a schema validator over the workers' scratch files); the runner itself judges every node by exit code alone.

6. **Zero-Token Short-Circuiting**:
   - Cheap deterministic checks (regex, file hashes, git status, schema checks) must always execute before expensive model inference calls.
   - Assign deterministic checks to type `verifier_gate` with tier `deterministic_script`.

7. **Executable Commands Only**:
   - The runner executes every `command_or_eval` with `bash -c`. `tier` is a planning label, not a dispatch mechanism: a `fast_engine` or `frontier_engine` node must invoke its model through a CLI inside the command (for example `claude -p "..." > "$GRAPH_SCRATCH_DIR/out.json"`).
   - `input_bindings` and `output_contract` are declarative. Nodes exchange data through files under `$GRAPH_SCRATCH_DIR/..` (sibling node directories), and enforcement belongs in a verifier or barrier command.

## 2. Token Economic Principles

1. **Compact Payload Protocol**:
   - Intermediate nodes must emit compact, lossy JSON payloads.
   - Never pass full conversational transcripts or multi-megabyte source traces between nodes.

2. **Compute Tier Allocation**:
   - Leaf nodes (extraction, classification, shallow scans) use `fast_engine` (for example, Gemini Flash or local models).
   - Deterministic validations use `deterministic_script` (Bash, Python validators, schema checkers).
   - Only complex synthesis, reconciliation, and conflict resolution nodes use `frontier_engine` (Gemini Pro, Claude Sonnet).
   - `token_ceiling_total` in the budget section is advisory to aid planning and scheduling bounds.

## 3. Heuristic DAG Validation Checks

Before finalizing `graph-manifest.json`, verify:

1. **Acyclicity**: Graph must contain zero cycles (topological sort passes).
2. **Deterministic Root**: Every root node must depend on known input payloads or deterministic events.
3. **Strict Total Mutation Order**: All `sequential_mutation` nodes must form a single, unambiguous sequential chain.
4. **Valid Fallbacks**: Any node with `failure_escalation: "fallback_node"` must define a valid `fallback_node_id` whose node has `role: "fallback"` and the same `type` as the primary. Fallback nodes are excluded from standard sequential scheduling and execute only when substituting for a failed primary node, after their own `depends_on` are complete. A fallback mutation must depend on exactly the same preceding mutations as its primary; it takes the primary's place in the chain.
5. **Mutation Containment**: Every mutation node must declare `mutation_targets` (relative file paths) and optional `forbidden_paths`. Boundaries are checked against what git reports, so writes to gitignored paths or outside the repository are not detected; keep such writes out of mutation commands.
6. **Verifier Binding**: `verifier_hash` is the SHA256 of the first file named in `command_or_eval` (so `python3 scripts/verify.py` binds `verify.py`), or of the command string when it names no file.
