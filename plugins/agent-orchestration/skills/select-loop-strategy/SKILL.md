---
name: select-loop-strategy
plugin: agent-orchestration
description: Selects the optimal agent orchestration topology using a deterministic 6-gate decision tree.
allowed-tools: Read, Bash
---

# Select Loop Strategy (`select-loop-strategy`)

Deterministic decision framework to select the right execution topology for any engineering or research task.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Pattern Comparison](#pattern-comparison)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Preserve skill identities**: Route by intent without altering skill boundaries.
- **Fail safe**: If the task requires human gates or rollbacks, always choose `graph-execution`.
- **Zero tool leakage**: Delegated inner workers must operate under tool and git restrictions.

## Quick start

```bash
# Evaluate topology selection against test fixtures
pytest plugins/agent-orchestration/tests/test_loop_strategies.py
```

## Workflow

Evaluate task characteristics sequentially:
1. **Approval Gates & Rollbacks?** -> `graph-execution` (State machine, receipts, worktrees).
2. **10+ Independent Bulk Tasks?** -> `agent-swarm` (Concurrent workers, zero shared state).
3. **Adversarial Critique Required?** -> `red-team-review` (Generator + critic until approved).
4. **Autonomous Meta-Learning?** -> `triple-loop-learning` (Friction logging + headless evals).
5. **Supervisor / Coding Sub-Agent?** -> `dual-loop` (or `co-pilot-loop` for fast pairing).
6. **Single-Agent Research?** -> `learning-loop` (Autonomous single-context loop).

## Pattern Comparison

| Pattern | Skill | Core Mechanics | Primary Use Case |
|---|---|---|---|
| **Solo Learning** | `learning-loop` | Single context, discovery -> synthesis | Research, documentation, spikes |
| **Adversarial** | `red-team-review` | Generator + multi-persona critics | Security audits, architecture |
| **Dual-Loop** | `dual-loop` | Outer Director <-> Inner Worker | Feature implementation, bug fixes |
| **Fast Pair** | `co-pilot-loop` | Claude (Director) + Flash Low | Cost-sensitive prototyping |
| **Parallel Swarm** | `agent-swarm` | Concurrent batch worker runners | Bulk migrations, mass doc updates |
| **Meta-Learning** | `triple-loop-learning` | Friction logging -> headless eval | Autonomous system optimization |
| **Graph Execution** | `graph-execution` | Deterministic DAG & rollback | High-assurance migrations |

## Verification

```bash
# Run loop strategy routing tests
pytest plugins/agent-orchestration/tests/test_loop_strategies.py -v
```

## References

- [PATTERN_GUIDE.md](references/PATTERN_GUIDE.md) — Comprehensive comparative pattern guide.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Verification criteria and contracts.
- [fallback-tree.md](references/fallback-tree.md) — Escalation paths for ambiguous routing.
