---
name: agent-swarm
description: "Parallel multi-agent execution pattern. Use when: work can be partitioned into independent tasks that N agents can execute simultaneously across worktrees. Includes routing (sequential vs parallel), merge verification, and correction loops."
---

# Agent Swarm

Parallel or pipelined execution across multiple agents and worktrees. The orchestrator partitions work, dispatches to agents, and verifies/merges the results.

## When to Use

- Large features that can be split into independent work packages
- Bulk operations (tests, docs, migrations) that benefit from parallelism
- Multi-concern work where specialists handle different aspects simultaneously

## Process Flow

1. **Plan & Partition** — Break work into independent tasks. Define boundaries clearly.
2. **Route** — Decide execution mode:
   - **Sequential Pipeline** — Tasks depend on each other (A → B → C)
   - **Parallel Swarm** — Tasks are independent (A | B | C)
3. **Dispatch** — Create a worktree per task. Assign each to an agent:
   - CLI agent (Claude, Gemini, Copilot)
   - Deterministic script
   - Human
4. **Execute** — Each agent works in isolation. No cross-worktree communication.
5. **Verify & Merge** — Orchestrator checks each worktree's output against acceptance criteria.
   - **Pass** → Merge into main branch
   - **Fail** → Generate correction packet, re-dispatch
6. **Seal** — Bundle all merged artifacts
7. **Retrospective** — Did the partition strategy work? Was parallelism effective?

## Worker Selection

Each worktree can be assigned to a different worker type based on task complexity:

| Worker | Best For |
|--------|---------|
| **High-reasoning CLI** (Opus, Ultra) | Complex logic, architecture |
| **Fast CLI** (Haiku, Flash) | Tests, docs, routine tasks |
| **Specialist CLI** | Security audit, QA, DB migration |
| **Deterministic Script** | Formatting, linting, data transforms |
| **Human** | Judgment calls, creative decisions |

## Constraints

- Each worktree must be fully self-contained
- No git operations from inner agents
- Orchestrator owns all merge decisions

## Diagram

See: [agent_swarm.mmd](../../resources/diagrams/agent_swarm.mmd)
