---
name: using-exploration-cycle
description: Use when starting any conversation - establishes how to find and follow the business exploration workflow.
---

# Using Exploration Cycle (`using-exploration-cycle`)

Front-door dispatcher ensuring all incoming conversation requests check active exploration state and route through the governed phased exploration workflow.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)

## Critical Constraints

1. **Subagent Exclusion**: If dispatched as an isolated subagent (via `dispatch.py`) to execute a specific task, skip this skill entirely.
2. **Mandatory State Gate**: Before answering any user message or scoping request, verify active exploration state. If a session is in progress, route through the active phase of `exploration-workflow`.
3. **Database Sovereignty**: The SQLite state database is the absolute authority; `exploration/exploration-dashboard.md` is a read-only projection. Never rely on conversational memory for gate passage.
4. **Proactive Review During Waits**: Review upstream phase artifacts (discovery plans, visual captures, specs) during subagent execution waits.

## Quick start

Check whether an active exploration dashboard exists:

```bash
test -f exploration/exploration-dashboard.md && cat exploration/exploration-dashboard.md || echo "No active exploration session"
```

## Workflow

1. **Inspect Dashboard**: Check for `exploration/exploration-dashboard.md`.
2. **Evaluate Status**:
   - If `Complete`: Session ended. Answer normally or offer new exploration.
   - If `In Progress`: Identify current phase and yield control to `exploration-workflow`. Never answer in freeform prose.
   - If absent: If prompt expresses exploration intent ("I want to build...", "explore..."), bootstrap session via `exploration-workflow`.
3. **Continuous Review**: During execution or agent waits, verify artifact consistency and cross-phase alignment.

## Verification

Verify exploration session state and dashboard synchronization:

```bash
python3 plugins/exploration-cycle-plugin/scripts/state_engine.py status
```
