---
concept: agent-harness-summary
source: plugin-code
source_file: agent-agentic-os/SUMMARY.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.123053+00:00
cluster: memory
content_hash: 48abb76ebb5e8cd0
---

# Agent Harness: Summary

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Agent Harness: Summary

## What This Is

A pragmatic developer harness that gives your agent three things working together:

1. **Structured memory hierarchy** - agents carry forward what they learned in previous sessions with deduplication, conflict detection, and size management above native auto-memory limits.
2. **Continuous improvement loop** - skills and workflows learn from session friction and improve with every execution. It leverages a feedback control system with a metric-based gate.
3. **Cross-IDE orchestration** - a shared event log with simple execution locks allows solo developers to comfortably orchestrate things across multiple IDEs (Cursor, VS Code, Windsurf) while preventing collisions.

Claude Code ships auto-memory, native hooks, and subagent coordination. This plugin provides an **opinionated discipline layer** on top of those primitives to connect different workspaces.

## Who This Is For

Developers running **long-horizon, multi-session workflows** — projects where Claude Code runs across days or weeks, multiple agents share context, and the quality of what gets remembered and improved directly affects every future session.

Not for single-session tasks (native auto-memory is enough), enterprise multi-machine deployments, or framework-agnostic portability requirements.

## The Feedback and Learning Layer (The Differentiator)

While many tools add memory to agents, fewer implement a true feedback control system. This plugin operates as a **learning layer for agent workflows**, running a reinforcement + supervised learning cycle at the **instruction level**.

How it works:

```text
Session runs -> errors and friction captured to events.jsonl
             -> Triple-Loop Orchestrator formulates learning hypothesis for a SKILL.md
             -> eval_runner.py (The Headless Evaluator) scores it against static evals/evals.json fixtures
             -> if DISCARD, agent automatically reverts via `git reset --hard`
             -> if KEEP, the improved instruction is retained for the next session
```

A **test registry** prevents re-testing falsified hypotheses so improvement cycles don't repeat dead ends.

> **Note on Architecture:** The system strictly implements the **Karpathy 3-File Autoresearch Framework**. This replaces earlier experimental proxy heuristics with a rigorous headless evaluation relying purely on `eval_runner.py` and static `evals.json`. Subjective "LLM mental testing" is strictly prohibited to combat "Agent Dementia" (Goodhart's Law).

**⚠️ Current Safety Limits:** While the keyword bloat issue is solved by headless baseline testing, the loop still operates directly in the developer's workspace without a heavily isolated sandbox mode. The agent's strict `git reset --hard` mandate mitigates risk, but it is not a true parallel shadow execution environment.

The validator (`eval_runner.py`) provides the supervised part: changes **must** pass an objective benchmark before they are applied. The loop is the reinforcement part: friction in use generates the training signal.

The Agentic OS plugin applies this loop to its own skills. The plugin improves itself using the same mechanism it teaches — a live demonstration, not documentation.

## Agent Signaling Patterns

The core turn-management patterns this plugin enables:

**Triple-Loop Learning System** - A unified architectural model where the outer loop (Orchestrator) is a supervisor that sets goals, manages memory, and triggers evaluation runs overnight. The inner loops (Strategic Planner and Tactical Executor) handle the iterative patching of code/skills. The entire stack communicates via shared memory and event logs without tight coupling.

**Background + foreground** - a foreground session agent does active work while a background agent (`Triple-Loop Retrospective`, `os-health-check`) runs asynchronously. Simple locks prevent collisions. The background agent's findings are available to the foreground agent in the next session through promot

*(content truncated)*

## See Also

- [[agent-harness-learning-layer-formerly-agentic-os]]
- [[research-summary-agent-operating-systems-agent-os]]
- [[research-summary-agent-operating-systems-aos]]
- [[os-health-check-sub-agent]]
- [[global-agent-kernel]]
- [[template-post-run-agent-self-assessment]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/SUMMARY.md`
- **Indexed:** 2026-04-17T06:42:09.123053+00:00
