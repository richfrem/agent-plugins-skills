# Routing, delegation and closure

Assesses incoming tasks, routes to specialized execution patterns, and enforces verification and closure.

## Constraints

- **Trust but verify**: Never blindly trust sub-agent outputs; mechanically run automated tests.

- **Inner loop isolation**: Inner Loop agents are strictly forbidden from running `git` commands.

- **Background execution**: Always redirect stdin (`< /dev/null`) when spawning sub-agents.

- **Zero autonomous merge**: Merging and pushing are strictly caller-managed. The orchestrator halts after verification and retrospective.

## Quick start

```bash
# Generate strategy packet for delegation
python3 scripts/agent_orchestrator.py packet --wp 001 --spec-dir handoffs
```

## Routing Decision Table

| Signal | Pattern | Follow |
|---|---|---|
| Security review, architecture decision, high risk | Adversarial Critique | [strategy-red-team-review.md](strategy-red-team-review.md) |
| Bounded code implementation, bug fix | Supervisor / Worker | [strategy-dual-loop.md](strategy-dual-loop.md) |
| Bulk migration, 10+ independent partitioned jobs | Parallel Swarm | [strategy-agent-swarm.md](strategy-agent-swarm.md) |
| Structural dependencies, parallel fan-out joined at barriers | Graph | [graph-planning.md](graph-planning.md), then [graph-execution.md](graph-execution.md) |
| Ambiguous routing, topology comparison | Decision Tree | strategy selection ([strategy-selection.md](strategy-selection.md)) |

## Workflow

1. **Assess & Route**: Match incoming signal against the Routing Decision Table.

2. **Package**: Author Task Packet via `agent_orchestrator.py packet`. For graph workflows, mandate compilation of `graph-manifest.json` via graph planning ([graph-planning.md](graph-planning.md)).

3. **Dispatch**: Dispatch inner worker into isolated worktree with stdin redirection (`< /dev/null`).

4. **Supervised Verify**: Audit diff and run tests via `agent_orchestrator.py verify`.

5. **Close & Retro**: Run `agent_orchestrator.py retro`. Stop after recording retrospective. Caller performs review, merge, and deployment.

## Verification

```bash
# Verify worker execution results
python3 scripts/agent_orchestrator.py verify --packet handoffs/task_packet_001.md --worktree .
# Ensure tests pass
pytest
```
