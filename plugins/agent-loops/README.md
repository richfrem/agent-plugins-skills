# Agent Loops: Execution Primitives

A framework-agnostic library of structural execution patterns for AI agents. 
From simple single-agent learning loops to complex parallel swarms and hierarchical meta-loops, this plugin provides the routing, structure, and Python execution engines required to orchestrate work reliably.

It provides "LEGO bricks" for orchestration — bringing industry-standard agentic patterns (like Routing, Review-Critique, Parallel Swarm, and Inner/Outer Delegation) into concrete, runnable loops.

> **Scope:** Designed to work with any CLI-accessible AI (Claude Code, Copilot CLI, Gemini CLI, local models). It strictly provides *how* to loop. It does **not** provide personas, memory persistence, or evaluation infrastructure.

---

## Is This For You?

**Good fit:**
- Developers who need robust, repeatable ways to execute multi-agent workflows
- Workflows that require work to be partitioned and run concurrently (`agent-swarm`)
- Tasks that require an outer planner delegating to an inner executor (`dual-loop`)
- Any system that needs an adversarial Red Team review loop before finalizing output

**Not a fit:**
- If you need persistent session memory or evaluation-gated continuous improvement (use `agent-agentic-os` instead, which runs on top of these loops)
- If you just need a prompt library (this plugin provides structural execution, not domain-specific personas)

---

## 🚀 Start Here

> **Every execution starts with one router:**
>
> ```bash
> /orchestrator
> ```
>
> Describe your trigger (a question, issue, research need, or work assignment). The orchestrator acts as a **Routing Agent**, assessing the task and automatically dispatching it to the correct execution primitive below.

---

## What's in the Box

### Front Door

| Component | Role |
|-----------|------|
| `orchestrator` | The Router (Routing Agent Pattern). Assesses the trigger and routes to the appropriate loop pattern. |

---

### Core Execution Patterns (The Primitives)

| Skill | Pattern | Description |
|-------|---------|-------------|
| `learning-loop` | 1. Single Agent (Loop Agent) | Self-directed research and synthesis. Linear execution. No inner agents or review gates. |
| `red-team-review` | 2. Review & Critique (Adversarial) | Research → bundle context → red team review → iterate in rounds until the output is approved. |
| `dual-loop` | 3. Sequential Agent (Manager/Worker) | Outer loop plans and delegates to an inner CLI agent via strategy packets, then verifies the output. |
| `agent-swarm` | 4. Parallel Agent (Concurrent execution) | Partitions work → dispatches to N agents across isolated workspaces → verifies and merges all outputs. |
| `triple-loop-learning` | 5. Hierarchical Meta-Loop | Orchestrates a 3-tier execution hierarchy: Outer (spawn planners) → Mid (partition work) → Inner (execute packets). |

---

### Python Execution Engines

The true power of this plugin lies in its robust Python execution scripts that back the patterns above:

| Engine | Role | Description |
|--------|------|-------------|
| `swarm_run.py` | Parallel Engine | Token-efficient batching, rate-limit backoff, and checkpoint resume logic for the `agent-swarm`. |
| `agent_orchestrator.py` | Sequential Engine | Provides reliable packet generation and verification steps for `dual-loop` without fragile LLM terminal parsing. |
| `closure_guard.py` | Safety Hook | Checks local state for a `closure_done: true` flag to prevent premature session termination. |

---

## Separation of Concerns & System Boundaries

This plugin enforces a strict framework-agnostic boundary. It does **not** own the following concerns:

| Concern | Owned By | Relationship |
|---------|----------|-------------|
| **Personas / System Prompts** | Calling Environment | `agent-loops` routes the work, but you supply the persona (e.g. from `.claude/prompts/` or your own plugins). |
| **Memory & Persistence** | `agent-agentic-os` | Loop output is returned to the caller. Deduplication and memory promotion are handled externally. |
| **Objective Evaluation** | `agent-agentic-os` | `triple-loop-learning` executes 3-tier mechanics, but the external caller provides the eval gate (KEEP/DISCARD). |
| **Context Bundling** | `context-bundler` | Generic dependency required by `red-team-review` and for compiling session artifacts. |

---

## Directory Structure

```text
agent-loops/
├── .claude-plugin/      # Plugin manifest
├── hooks/               # Lifecycle hooks (closure enforcement via closure_guard.py)
├── assets/resources/
│   ├── diagrams/        # Architecture diagrams
│   └── templates/       # Structural templates (strategy-packets, generic retrospectives)
├── scripts/             # Core execution engines (swarm_run.py, agent_orchestrator.py)
├── skills/
│   ├── orchestrator/         # Routes to patterns
│   ├── learning-loop/        # Primitive 1
│   ├── red-team-review/      # Primitive 2
│   ├── dual-loop/            # Primitive 3
│   ├── agent-swarm/          # Primitive 4
│   └── triple-loop-learning/ # Primitive 5
└── references/          # Pattern guide and generic execution protocols
```

---

## Part of the Plugin Triad

| Plugin | Role |
|--------|------|
| `agent-scaffolders` | Spec + Factory — what ecosystem artifacts are and how to create them |
| `agent-agentic-os` | Operations — eval-gated improvement loop, experiment log, memory |
| **`agent-loops`** | **Execution patterns — the loop substrate used by the ecosystem** |
