# Learning Loop — Pattern Overview

**Industry standard**: Loop Agent / Single Agent
**Diagram**: [learning_loop.mmd](../assets/diagrams/learning_loop.mmd)
**Full skill reference**: [learning-loop-skill.md](learning-loop-skill.md)

---

## What It Is

The Learning Loop is a single-agent cognitive continuity protocol. One agent runs a structured
research-and-synthesis cycle, persisting knowledge across isolated sessions so the next agent
starts informed rather than blind.

Use it for: solo research sessions, knowledge capture, orientation at session start, and
retrospective closure at session end.

---

## Structure

```
Trigger
  -> Orient (load prior context from RLM cache or state file)
  -> Cognitive Synthesis
       Research -> Document -> Iterate?
                                  Yes -> Deepen -> Research
                                  No  -> Completion
  -> Handoff to Orchestrator -> Retrospective & Closure
```

The loop is entirely self-contained. No sub-agents are spawned. The agent both plans and
executes, cycling through research and documentation until the goal is met.

---

## Key Phases

| Phase | Name | What Happens |
|---|---|---|
| I | Orientation | Load context from last session (state file, RLM cache). Report readiness. |
| II | Intelligence Synthesis | Research, aggregate findings into structured markdown. |
| III | Strategic Gate | Present findings to user. Wait for explicit approval before proceeding. |
| IV | Red Team Audit | Compile research packet, submit for adversarial critique. Gate on "Ready" verdict. |
| Execution | Standard or Delegated | Either agent executes directly (Option A) or delegates to Dual-Loop (Option B). |
| V | Self-Assessment Survey | Answer every section — friction events, uncertainty, improvement recommendation. |
| VI | Post-Run Metrics | Run automated metric collector. Feed improvement loop. |
| VII | Memory Persistence | Write dated session log, promote key findings to long-term memory. |
| VIII | Handoff | Confirm exit conditions met, return control to Orchestrator. |

---

## When to Use in the Exploration Cycle

- **Phase A solo sessions**: when one agent alone drives the full discovery pass
- **Orientation at session start**: always — before touching any code or artifacts
- **Closure at session end**: always — skip it and the next agent starts blind
- **When Dual-Loop is overkill**: no delegation needed, single agent can handle full synthesis

---

## Relationship to Dual-Loop

The Learning Loop contains the Dual-Loop as an optional execution branch (Phase IV Option B).
When delegation is needed, the Learning Loop (Outer Loop) generates a Strategy Packet and
hands off to the Dual-Loop inner agent. All cognitive continuity — orientation, memory,
retrospective — remains the Learning Loop's responsibility.

See [triple-loop-architecture.md](triple-loop-architecture.md) for the delegation pattern.
