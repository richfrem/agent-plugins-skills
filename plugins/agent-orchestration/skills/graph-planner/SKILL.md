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
   - Converge parallel branches at a `sync_barrier`.
   - Allocate `fast_engine` for leaf nodes and `frontier_engine` for synthesis.

4. **Compile Manifest**: Author `graph-manifest.json` adhering to `graph-manifest-schema.json`. Include Mermaid visualization diagram in plan notes.

5. **Validate & Handoff**: Run `validate_manifest.py`. Present compiled manifest to caller environment for review and execution handoff.

## Verification

```bash
# Deterministic manifest validation
python3 scripts/validate_manifest.py graph-manifest.json --check-approval-none
```

## References

- [graph-manifest-schema.json](references/graph-manifest-schema.json): Canonical manifest schema contract.
- [topology-rules.md](references/topology-rules.md): Structural topology rules and token economics.
- [acceptance-criteria.md](references/acceptance-criteria.md): Verification criteria and gate definitions.
