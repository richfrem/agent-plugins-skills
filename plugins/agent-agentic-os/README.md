# Agent Harness & Learning Layer (formerly Agentic OS)

A developer harness that gives your AI agent **persistent memory**, a **feedback and learning loop**, and **cross-IDE orchestration** — helping solo developers coordinate workflows and continuously improve skills with every execution across multiple environments (VS Code, Cursor, Windsurf, Copilot).

> **Positioning:** Anthropic now ships auto-memory, native hooks, and subagent coordination natively. This plugin is not an operating system, but rather an **opinionated discipline layer** on top of those primitives. It provides a structured memory hierarchy, continuous workflow improvement, and an event log for cross-platform agent signaling. See [`SUMMARY.md`](./SUMMARY.md) for full context and known limitations.

---

## The Problem

Claude Code ships persistent memory. What it gives you is a 200-line `MEMORY.md` with no structured deduplication, no promotion logic, and no eval gate. That works for a few sessions. It breaks down when you have multiple agents, background loops, and workflows that span days or weeks where the quality of what gets remembered directly affects the quality of every future session.

The harder problem: coordination. How does the background improvement agent share what it learned with the foreground session? How does an outer-loop supervisor pass context to an inner-loop worker? How do two agents write to shared memory without corrupting it?

This plugin provides a system for that.

---

## What It Does

### Structured Memory Hierarchy

Every session writes structured logs to `context/events.jsonl` and `context/memory/`. At end-of-session, the `session-memory-manager` deduplicates and promotes important facts to `context/memory.md` - a curated long-term store that bootstraps every future session. Dedup IDs, conflict detection, and size limits prevent the memory from drifting into contradiction over hundreds of sessions.

### Continuous Improvement Loop (The Learning Layer)

This is the system's core differentiator: a feedback control system for agent workflows. It doesn't just manage memory—it continuously improves the instructions the model receives based on objective evaluation. 

```
Session runs
  -> errors and friction logged to events.jsonl
  -> os-learning-loop mines the event log
  -> proposes patches to SKILL.md files and CLAUDE.md
  -> skill-improvement-eval scores the patch against evals/evals.json
  -> patch applied ONLY if objective score improves
  -> next session runs with better instructions
```

> **⚠️ Experimental Warning (Round 2 Red-Team findings):** The current eval gate relies on a keyword-overlap heuristic, which risks over-optimizing for keyword bloat (Goodhart's Law). Furthermore, the loop operates without an isolated validation environment (shadow mode). Treat the `auto-apply` zone with caution and perform manual reviews of changes to your `SKILL.md` files until semantic embedding evaluations are fully integrated.

A test registry prevents re-testing falsified hypotheses — improvements accumulate without repeating dead ends. The plugin applies this loop to its own skills: it is a live lab as much as a tool.

### Agent Signaling and Turn Management

Three simple signaling patterns built into the system:

**Inner/outer loop** - outer supervisor sets goals and reviews results; inner worker executes and signals completion in the shared event log. Context flows through shared memory, not tight coupling.

**Background + foreground** - background agents (`os-learning-loop`, `os-health-check`) run asynchronously with simple execution locks preventing collisions. Their findings surface in the next foreground session through promoted memory.

**Sequential agent handoff** - Agent A writes structured output to the event log. Agent B reads the log to pick up where A left off. Agents coordinate their turns through the simple shared log, not through each other.

---

## Who This Is For

Developers running **long-horizon, multi-session workflows** — projects where Claude Code runs across days or weeks, with multiple agents that need to build on each other's context.

This is NOT for:
- Single-session tasks (native auto-memory is sufficient)
- Enterprise multi-machine deployments (see `references/vision.md`)
- Framework-agnostic portability requirements

---

## Scope

- **Developer tool, single machine** - designed and tested for solo developer use
- **No external dependencies** - file system only, standard library Python
- **Academic/research quality** - clarity of implementation over production hardening
- **Not enterprise scale** - for multi-machine coordination or high-throughput streaming, see `references/vision.md`

---

## Installation

### From the Marketplace (Recommended)
```bash
/plugin marketplace add richfrem/agent-plugins-skills
/plugin install agent-agentic-os
```

### From GitHub Directly
```bash
# Full plugin (Claude Code)
/plugin marketplace add richfrem/agent-plugins-skills
/plugin install agent-agentic-os

# Skills only (portable, works with Claude, Copilot, Gemini CLI)
npx skills add richfrem/agent-plugins-skills --path plugins/agent-agentic-os
```

### Local Development
```bash
/plugin marketplace add ./
/plugin install agent-agentic-os
```

---

## Quick Start

After installation, ask your agent:

```
"Set up an agentic OS for this project"
```

The `agentic-os-setup` agent runs a discovery interview and scaffolds the environment. Then:

```bash
/os-loop      # run improvement retrospective after a session
/os-memory    # manually trigger memory promotion
/os-init      # re-initialize or repair the environment
```

---

## Plugin Components

### Skills

| Skill | Purpose |
|-------|---------|
| `agentic-os-guide` | Full reference: all layers, interactions, and patterns explained |
| `agentic-os-init` | Scaffolds a new OS environment via discovery interview |
| `session-memory-manager` | Deduplicates and promotes session facts to long-term memory |
| `skill-improvement-eval` | Scores proposed skill patches against objective evals before applying |
| `os-clean-locks` | Removes stale execution locks that block agent execution |
| `concurrent-agent-loop` | Coordinates parallel agents through the shared event log |
| `loop-progress-report` | Generates improvement metrics from eval history |
| `todo-check` | Audits files for unresolved TODO items |

### Agents

| Agent | Purpose |
|-------|---------|
| `agentic-os-setup` | Conversational setup guide; runs the init interview |
| `os-learning-loop` | Post-session retrospective; mines friction, proposes and validates skill patches |
| `os-health-check` | System diagnostics; inspects event log, memory state, lock status |

### Hooks

`hooks/hooks.json` registers hooks:
- `post_run_metrics.py` - captures session errors and friction events to the event log automatically
- `update_memory.py` - triggers memory promotion after significant sessions

### Commands

| Command | Purpose |
|---------|---------|
| `/os-init` | Initialize or repair the OS environment |
| `/os-loop` | Run the improvement loop retrospective |
| `/os-memory` | Manually run memory management |

---

## Architecture

The OS metaphor explains the design: the context window is finite RAM. Every byte consumed by infrastructure is a byte unavailable for actual work. The architecture is built around that constraint.

```
CONTEXT WINDOW (RAM - finite, cleared every session)
  Always present: skill metadata headers, CLAUDE.md, soul.md, user.md

DISK (context/ folder - persistent across sessions)
  context/memory.md          <- L3 long-term curated facts
  context/memory/YYYY-MM-DD.md  <- L2 session logs
  context/events.jsonl       <- event log / audit trail
  context/os-state.json      <- system registry
  context/.locks/            <- execution locks

SKILLS (loaded into RAM only when triggered)
  skills/*/SKILL.md          <- full body stays on disk until invoked

HOOKS (fire on every tool call)
  PreToolUse                 <- inspect, block, or log before execution
  PostToolUse                <- audit results, capture metrics
```

For the full OS analogy table and three-tier lazy loading details, see [`SUMMARY.md`](./SUMMARY.md).

### Architecture Diagrams

| Diagram | Description |
|---------|-------------|
| ![Overview](./assets/diagrams/agentic-os-overview.png) | Conceptual OS structure |
| ![Structure](./assets/diagrams/agentic-os-structure.png) | Physical plugin architecture |
| ![Loop lifecycle](./assets/diagrams/agentic-os-loop-lifecycle.png) | Improvement loop sequence |
| ![Memory subsystem](./assets/diagrams/agentic-os-memory-subsystem.png) | Memory promotion flowchart |

---

## Part of the Plugin Triad

| Plugin | Role |
|--------|------|
| `agent-skill-open-specifications` | Spec - what ecosystem artifacts are |
| `agent-scaffolders` | Factory - how to create them |
| **`agent-agentic-os`** | **Operations - how to run and improve the environment** |

---

## Key References

- [`SUMMARY.md`](./SUMMARY.md) - scope, architecture, OS analogy, how-to
- [`references/vision.md`](./references/vision.md) - where this pattern is heading; what enterprise and hyperscaler solutions will need to solve
- [`references/dual-loop.md`](./references/dual-loop.md) - inner/outer loop coordination patterns
- [`references/memory-hygiene.md`](./references/memory-hygiene.md) - when to write, promote, archive, and expire
- [Anthropic CLAUDE.md docs](https://docs.anthropic.com/en/docs/claude-code/memory)
- [Anthropic /loop scheduler](https://docs.anthropic.com/en/docs/claude-code/loop)
