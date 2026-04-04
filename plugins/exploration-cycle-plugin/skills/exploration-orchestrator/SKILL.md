---
name: exploration-orchestrator
description: >-
  Coordinates the multi-agent exploration loop, manages state, routes work to
  specialized skills or agents, triggers narrowing reviews, and decides when to
  continue exploration, prepare handoff, or reopen discovery from engineering.
  Trigger with "start exploration", "coordinate the discovery phase", "manage the
  exploration loop", or "route work to specialized exploration agents".
allowed-tools: Bash, Read, Write
---

# Exploration Orchestrator

> ⚠️ **STUB** — `execute.py` not yet implemented.
> Use the [exploration-cycle-orchestrator-agent](../../agents/exploration-cycle-orchestrator-agent.md) for the real logic.
> [See acceptance criteria](./acceptance-criteria.md)

## Purpose

This skill coordinates the Phase A exploration cycle. It selects an appropriate next action,
routes work to the right specialized agent, and manages exploration state.

## Correct Behavior

- Starts broad exploration when the problem or solution is still unclear
- Routes work to the right specialized agent when a specific artifact is needed
- Triggers narrowing only when confidence appears sufficient
- Reopens exploration when engineering ambiguity is real
