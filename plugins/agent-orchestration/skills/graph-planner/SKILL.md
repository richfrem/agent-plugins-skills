---
name: graph-planner
plugin: agent-orchestration
description: Interactively interviews the user to architect, topologically validate, and compile token-budgeted execution graphs (DAGs) with explicit parallel/sequential boundaries, short-circuit gates, and verifiable contracts. Use when designing multi-step agentic workflows, DAGs, or task pipelines.
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Graph Planner (`graph-planner`)

Architects, topologically validates, and compiles token-budgeted execution graphs (DAGs) into `graph-manifest.json`.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Ingest Before Interview**: Read caller briefs or task specifications first; ask user questions only on unresolved topological gaps.

- **Zero Parallel Mutations**: Side-effecting mutations must always form a strict linear chain.

- **Read-Only DAGs Valid**: Graphs with zero mutations (pure parallel reads and join barriers) are valid for spikes and discovery.

- **Deterministic Gates**: Use `verifier_gate` with `tier: "deterministic_script"` before expensive model calls.

- **Executable Commands**: `graph-execution` runs every `command_or_eval` with `bash -c`. Model-tier nodes must call a CLI inside the command and write output to `$GRAPH_SCRATCH_DIR`; never put a bare prompt in `command_or_eval`.

- **Gate Irreversible Actions**: Nodes with external side effects set `reversible: false` and depend on the approval gate.

## Quick start

```bash
# Validate compiled manifest against schema and acyclicity rules
python3 scripts/validate_manifest.py graph-manifest.json
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

4. **Compile Manifest**: Author `graph-manifest.json` adhering to `graph-manifest-schema.json`. For each `verifier_hash`, hash the first file named in the command (`shasum -a 256 scripts/verify.py`), or the command string when it names no file. Write a Mermaid diagram of the DAG next to the manifest (or in the task plan) and show it to the caller.

5. **Validate & Handoff**: Run `validate_manifest.py` (add `--check-approval-none` when the graph will run with `--approval none`). Hand off the manifest path, its SHA256 (`shasum -a 256 graph-manifest.json`), the intended `--approval` mode, and the workspace flag. The human approves that SHA; any later manifest edit requires re-approval.

## Verification

```bash
# Deterministic manifest validation
python3 scripts/validate_manifest.py graph-manifest.json

# Additionally required for manifests that will run with --approval none
python3 scripts/validate_manifest.py graph-manifest.json --check-approval-none
```

## References

- [graph-manifest-schema.json](references/graph-manifest-schema.json): Canonical manifest schema contract.
- [topology-rules.md](references/topology-rules.md): Structural topology rules and token economics.
- [acceptance-criteria.md](references/acceptance-criteria.md): Verification criteria and gate definitions.
- [graph-planner-flow.mmd](graph-planner-flow.mmd): Planner workflow diagram.
