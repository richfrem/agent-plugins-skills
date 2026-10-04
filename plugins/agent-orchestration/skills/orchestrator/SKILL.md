---
name: orchestrator
plugin: agent-orchestration
description: "(Industry standard: Routing Agent / Orchestrator Pattern) Analyzes incoming triggers to select loop patterns and manage shared session closure."
allowed-tools: Bash, Read, Write
---

## Dependencies

Requires Python 3.8+ (standard library only).

---

# Orchestrator (`orchestrator`)

Assesses incoming tasks, routes to specialized execution patterns, and enforces verification and closure.

## Contents

- [Dependencies](#dependencies)
- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Routing Decision Table](#routing-decision-table)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Trust but verify**: Never blindly trust sub-agent outputs; mechanically run automated tests.

- **Inner loop isolation**: Inner Loop agents are strictly forbidden from running `git` commands.

- **Background execution**: Always redirect stdin (`< /dev/null`) when spawning sub-agents.

- **Zero autonomous merge**: Merging and pushing are strictly caller-managed. The orchestrator halts after verification and retrospective.

## Quick start

```bash
# Generate strategy packet for delegation
python ./scripts/agent_orchestrator.py packet --wp 001 --spec-dir handoffs
```

## Routing Decision Table

| Signal | Pattern | Delegated Skill |
|---|---|---|
| Exploratory research, single-context task | Solo Loop | `learning-loop` |
| Security review, architecture decision, high risk | Adversarial Critique | `red-team-review` |
| Bounded code implementation, bug fix | Supervisor / Worker | `dual-loop` |
| Bulk migration, 10+ independent partitioned jobs | Parallel Swarm | `agent-swarm` |
| Unguided friction evaluation, autonomous evals | Meta-Learning | `triple-loop-learning` |
| Structural dependencies, parallel fan-out joined at barriers | Graph | `graph-planner` -> `graph-execution` |
| Ambiguous routing, topology comparison | Decision Tree | `select-loop-strategy` |

## Workflow

1. **Assess & Route**: Match incoming signal against the Routing Decision Table.

2. **Package**: Author Task Packet via `agent_orchestrator.py packet`. For graph workflows, mandate compilation of `graph-manifest.json` via `graph-planner`.

3. **Dispatch**: Dispatch inner worker into isolated worktree with stdin redirection (`< /dev/null`).

4. **Supervised Verify**: Audit diff and run tests via `agent_orchestrator.py verify`.

5. **Close & Retro**: Run `agent_orchestrator.py retro`. Stop after recording retrospective. Caller performs review, merge, and deployment.

## Verification

```bash
# Verify worker execution results
python ./scripts/agent_orchestrator.py verify --packet handoffs/task_packet_001.md --worktree .
# Ensure tests pass
pytest
```

## References

- [cli-agent-executor.md](references/cli-agent-executor.md) - Specialized CLI personas.
- [acceptance-criteria.md](references/acceptance-criteria.md) - Phase gates and exit criteria.
- [fallback-tree.md](references/fallback-tree.md) - Recovery protocols for loop stalls.
