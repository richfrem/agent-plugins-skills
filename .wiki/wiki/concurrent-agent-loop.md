---
concept: concurrent-agent-loop
source: plugin-code
source_file: agent-agentic-os/skills/os-improvement-loop/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.716471+00:00
cluster: plugin-code
content_hash: 6992396ef92dc5f2
---

# Concurrent Agent Loop

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: os-improvement-loop
version: 0.5.0
description: >
  Pattern 5: Concurrent Event-Driven Multi-Agent Loop. Coordinates multiple Claude sessions
  as OS threads sharing a common event bus and memory address space. Every loop cycle is a
  full improvement cycle: execute, eval against benchmark (KEEP/DISCARD), emit friction events
  during work, close with post_run_metrics, agent self-assessment survey saved to retrospectives,
  memory persistence, and Triple-Loop Retrospective trigger if friction threshold crossed.
  Four coordination topologies: turn-signal, fan-out, request-reply, triple-loop (Pattern D).
status: active
trigger: concurrent agents, shared event log, parallel agents, turn signal, fan-out,
  request-reply, background task shared state, event-driven agents, agent threads, kernel event bus,
  cross-session coordination, replace AGENT_COMMS, concurrent skill audit, claim task,
  inner agent, orchestrator peer agent, worker agent, continuous improvement loop,
  eval benchmark, self-assessment survey, post-run survey, friction events, metrics,
  Triple-Loop Retrospective, skill improvement, memory persistence, retrospective
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Concurrent Agent Loop

> Pattern 5 in the agent-loops taxonomy. Treats concurrent Claude sessions as OS threads
> sharing a filesystem address space. The kernel event bus coordinates signals. Every cycle
> includes real work, eval against benchmark, friction tracking, agent self-assessment survey,
> post-run metrics, and memory persistence. The OS learns from every run.

---

## Triple-Loop Architecture

There are **two distinct Triple-Loop orchestration cycles** operating at different scopes. Do not conflate them.

```
┌─────────────────────────────────────────────────────────┐
│  TRIPLE-LOOP ARCHITECT — OS Self-Improvement (this skill)       │
│                                                          │
│  os-improvement-loop evaluates and improves the OS       │
│  workflows, protocols, agent coordination patterns,      │
│  and this SKILL.md itself.                               │
│                                                          │
│  Target: the OS machinery — ledgers, surveys, kernel,    │
│  event bus, loop protocol.                               │
│  Eval gate: ORCHESTRATOR + PEER_AGENT run eval_runner.py │
│  on the OS skill being patched.                          │
│  Self-improvement: ORCHESTRATOR updates this SKILL.md    │
│  when a confirmed protocol fix is found.                 │
└────────────────────┬────────────────────────────────────┘
                     │ spawns / governs
┌────────────────────▼────────────────────────────────────┐
│  TRIPLE-LOOP EXECUTOR — Individual Skill Improvement           │
│                                                          │
│  os-eval-runner evaluates and improves a specific        │
│  target SKILL.md (routing accuracy,                     │
│  trigger descriptions, example blocks).                  │
│                                                          │
│  Target: a single skill's description and routing.       │
│  Eval gate: os-eval-runner scores the target skill.      │
│  Improvement: os-eval-runner runs RED-GREEN-REFACTOR     │
│  until score ≥ threshold.                                │
└─────────────────────────────────────────────────────────┘
```

**Key distinction:**
- The OUTER loop asks: *"Is the OS improvement process itself working correctly?"*
- The INNER loop asks: *"Does this specific skill route and execute correctly?"*

**`Triple-Loop Retrospective` vs `os-improvement-loop`:** `Triple-Loop Retrospective` (agent) is the
trigger/diagnostic layer — it analyzes friction events, identifies improvement targets,
and decides which Triple-Loop to invoke. `os-improvement-loop` (skill) is the execution
protocol that agents follow once a target has been identified. Do not conflate them.

**Session Lifecycle Invariant**: The OUTER loop owns session lifecycl

*(content truncated)*

## See Also

- [[dual-loop-innerouter-agent-delegation]]
- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[agent-agentic-os-hooks]]
- [[agent-bridge]]
- [[agent-harness-learning-layer]]
- [[agent-loops-execution-primitives]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/skills/os-improvement-loop/SKILL.md`
- **Indexed:** 2026-04-27T05:21:03.716471+00:00
