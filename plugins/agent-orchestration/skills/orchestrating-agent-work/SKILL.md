---
name: orchestrating-agent-work
plugin: agent-orchestration
description: >
  Interactive orchestrator for complex engineering work. Analyzes the task, conducts a
  diagnostic interview to select the appropriate execution strategy (Directed Acyclic Graph
  versus Loop, and which Loop type), plans the artifact, and supervises execution and verification.
  Use for "how should I orchestrate this", "plan this workflow", "should this be a DAG or a loop",
  "run these jobs in parallel", "delegate this to a worker agent", or "run/resume this graph
  manifest". Not for single trivial edits or skill self-improvement.
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Orchestrating Agent Work (`orchestrating-agent-work`)

Interactive front door: analyze the task, conduct diagnostic interview, select Graph vs. Loop, plan, execute, and verify.

## Contents

- [Dependencies](#dependencies) • [Constraints](#constraints) • [Quick Start](#quick-start) • [Workflow](#workflow) • [Strategies](#strategies) • [Verification](#verification) • [References](#references)

## Dependencies

Requires Python 3.8+ (standard library only).

## Constraints

- **Interactive Confirmation**: Ask at most 3 questions (one per turn) for ambiguous dimensions; present structured choices with `Option A [Recommended]`; human confirms or overrides selection before planning.
- **Topology First (Graph vs. Loop)**: Choose Graph (DAG) for distinct steps, parallel fan-out reads, or ordering barriers; choose Loop for iterative delegation.
- **Trust but Verify**: Never accept worker output without running automated test suites and auditing the git diff.
- **Loop Isolation**: Inner execution loops are strictly forbidden from running `git` write commands (commits and merges stay with caller).
- **Confinement & Redirection**: Workspace mutations run in an isolated worktree; background CLI calls redirect stdin (`< /dev/null`).
- **Human Gate Integrity**: Graph runs with `--approval none` require an explicit human-approved manifest SHA; never self-sign manifests you wrote.

## Quick Start

```bash
python3 scripts/select_strategy.py --out docs/plans/work-tasks/<task-id>/
python3 scripts/validate_manifest.py graph-manifest.json
python3 scripts/graph_runner.py graph-manifest.json --worktree .worktrees/task-<id> --approval prompt
```

## Workflow

1. **Analyze**: Ingest requirements, evaluate dependency structure, ordering barriers, concurrency, and risk ([routing-and-closure.md](references/routing-and-closure.md)).
2. **Interview & Select**: Ask 1–3 structured questions; run `select_strategy.py`; present **Graph (DAG)** vs **Loop** (Dual-Loop vs Swarm); confirm human agreement ([strategy-selection.md](references/strategy-selection.md)).
3. **Plan**:
   - **Graph (DAG)**: Compile and validate `graph-manifest.json` ([graph-planning.md](references/graph-planning.md), [topology-rules.md](references/topology-rules.md)).
   - **Dual-Loop**: Author `handoffs/task_packet_<id>.md` with atomic scope and "NO GIT" rule ([strategy-dual-loop.md](references/strategy-dual-loop.md)).
   - **Parallel Swarm**: Partition tasks into independent units; author `<id>.job.md` ([strategy-agent-swarm.md](references/strategy-agent-swarm.md)).
4. **Execute**:
   - **Graph**: Run state machine via `graph_runner.py` with worktree isolation and rollback ([graph-execution.md](references/graph-execution.md)).
   - **Dual-Loop**: Dispatch tactical coding worker into isolated worktree with stdin redirection (`< /dev/null`).
   - **Parallel Swarm**: Run `swarm_run.py` with resume support.
5. **Verify & Close**: Run test suites, audit diffs (`agent_orchestrator.py verify`), and complete retrospective survey before completion.

## Strategies

| Strategy | When to Choose | Plan Artifact | Reference |
|---|---|---|---|
| `direct` | Minimal localized edit without sub-agent overhead | Implementation plan | [routing-and-closure.md](references/routing-and-closure.md) |
| `graph` | Distinct dependent steps, parallel fan-out reads, join barriers, ordered mutations | `graph-manifest.json` | [graph-planning.md](references/graph-planning.md), [graph-execution.md](references/graph-execution.md) |
| `dual-loop` | One bounded task; outer supervisor orchestrates tactical inner worker | `handoffs/task_packet_<id>.md` | [strategy-dual-loop.md](references/strategy-dual-loop.md) |
| `agent-swarm` | Many identical independent tasks partitioned across bulk files or items | `<id>.job.md` | [strategy-agent-swarm.md](references/strategy-agent-swarm.md) |

## Verification

```bash
python3 scripts/agent_orchestrator.py verify --packet handoffs/task_packet_<id>.md --worktree .
cat "$(git rev-parse --git-common-dir)/graph-run/<graph_id>/<run_id>/state.json"
```

Consult matching section in [acceptance-criteria.md](references/acceptance-criteria.md); on failure use [fallback-tree.md](references/fallback-tree.md).

## References

- Steps: [routing-and-closure.md](references/routing-and-closure.md) • [strategy-selection.md](references/strategy-selection.md) • [graph-planning.md](references/graph-planning.md) • [graph-execution.md](references/graph-execution.md)
- Strategies: [strategy-dual-loop.md](references/strategy-dual-loop.md) • [strategy-agent-swarm.md](references/strategy-agent-swarm.md)
- Contracts: [topology-rules.md](references/topology-rules.md) • [graph-manifest-schema.json](references/graph-manifest-schema.json) • [PATTERN_GUIDE.md](references/PATTERN_GUIDE.md) • [patterns.json](references/patterns.json) • [cli-agent-executor.md](references/cli-agent-executor.md) • [cheapest_models.md](references/cheapest_models.md) • [post_run_survey.md](references/post_run_survey.md)
- Architecture: [orchestrating_agent_work_architecture.mmd](references/diagrams/orchestrating_agent_work_architecture.mmd) • [acceptance-criteria.md](references/acceptance-criteria.md) • [fallback-tree.md](references/fallback-tree.md)
