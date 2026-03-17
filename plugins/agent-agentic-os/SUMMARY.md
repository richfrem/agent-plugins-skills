# Agentic OS: Executive Summary

## What is the Agentic OS Plugin?
The **Agentic OS** plugin is a foundational scaffolding framework that transforms a standard project repository into a persistent, multi-agent environment. It bridges the gap between ephemeral conversational AI sessions and long-term, autonomous agent operations (such as those performed by Claude Code or GitHub Copilot CLI). 

Using a traditional Operating System metaphor, the plugin scaffolds a robust architecture directly into the host project:
* **The Kernel (`CLAUDE.md` & `context/kernel.py`)**: Acts as the central nervous system — `CLAUDE.md` defines rules loaded every session, `kernel.py` manages atomic file locks, system state, and event routing.
* **RAM (the context window)**: The active context window is the real RAM — finite, wiped every session. What always occupies this RAM is skill metadata (name + description headers), agent descriptions, `CLAUDE.md`, `soul.md`, and `user.md`. Full skill bodies and reference docs stay on disk until needed.
* **Disk Storage (`context/`)**: Persistent storage across sessions. Contains the system registry (`os-state.json`), event log (`events.jsonl`), L2 session logs (`context/memory/YYYY-MM-DD.md`), L3 long-term memory (`context/memory.md`), and mutex locks (`context/.locks/`). Nothing here occupies the context window unless explicitly loaded.
* **Installed Applications (`skills/`)**: Full `SKILL.md` bodies live on disk. A skill's metadata header is always in RAM for routing; the full body only loads into the context window when that skill is triggered — identical to how an OS loads an application from disk into RAM on launch.
* **Event Bus (`context/events.jsonl`)**: The system-wide audit trail — analogous to a UNIX syslog or Windows Event Log. Agents emit structured JSONL events (`intent`, `result`, `error`, `learning`) via `kernel.py`'s `emit_event()` command. The bus is append-only during normal operation; `os-health-check` reads it for diagnostics and `os-learning-loop` mines it for improvement signals. It never enters the context window unless explicitly read for audit purposes.
* **Background Daemons (`agents/`)**: Specialized sub-agents like `os-learning-loop` (continuous improvement), `os-health-check` (system metrics), and `session-memory-manager` (deduplicating and promoting facts) — each runs autonomously, acquires a mutex lock, performs its work, and terminates.
* **Security Sentinels (`hooks/`)**: Event-driven interceptors that fire before and after every tool call. `PreToolUse` hooks act as a kernel security module — they inspect the incoming operation (file write, shell command, git push) and can block, modify, or log it before it executes. `PostToolUse` hooks audit the result. Together they form a real-time enforcement layer: blocking destructive commands, validating outputs against policy, alerting on anomalous patterns, and preventing any agent — including a misbehaving or prompt-injected one — from taking actions outside its defined authority.

### Three-Tier Lazy-Loading Pattern

The entire architecture is designed around one constraint: **the context window is finite RAM**, and every byte of it consumed by infrastructure is a byte unavailable for actual work.

The system implements a three-tier lazy-loading strategy to maximize working memory:

| Tier | What | When it enters RAM |
|------|------|--------------------|
| **Always loaded** | Skill metadata headers, agent descriptions, `CLAUDE.md`, `soul.md`, `user.md` | Every session — required for routing and identity |
| **Loaded on trigger** | Full `SKILL.md` body (phases, logic, instructions) | Only when that specific skill is invoked |
| **Loaded on demand** | `references/` documents via progressive disclosure | Only when a specific sub-topic is needed within an active skill |
| **Loaded for audit/diagnosis** | `context/events.jsonl` (event bus) | Only when `os-health-check` or `os-learning-loop` explicitly reads the log — never loaded during normal agent work |

This is why `CLAUDE.md` has a 300-line discipline, skill descriptions are deliberately tight, and `references/` files are fetched individually via `@import` rather than loaded wholesale. The `context/` folder is disk — not RAM. Session logs, `memory.md`, and `os-state.json` are only pulled into the context window when explicitly needed, keeping the agent's working memory as clear as possible.

### OS Analogy Reference Table

| Real OS | Agentic OS |
|---------|------------|
| Kernel | `CLAUDE.md` + `kernel.py` — rules loaded every session + concurrency manager |
| RAM (finite, clears on shutdown) | The active context window — finite, clears every session |
| What's always loaded in RAM | Skill metadata (name + description headers only), agent descriptions, `CLAUDE.md`, `soul.md`, `user.md` |
| Installed application on disk | Full `SKILL.md` body (phases, logic, instructions) — stays on disk until invoked |
| App launcher / Start menu | Skill metadata descriptions — scanned to decide which skill to invoke |
| Opening an application | A skill being triggered — full body loads into context window (RAM) |
| DLL / library loaded on demand | `references/` files fetched via progressive disclosure — only the specific doc needed, only when needed |
| Background daemon / service | Agents (`os-learning-loop`, `os-health-check`) — runs autonomously, acquires locks, terminates |
| Cron scheduler | `/loop` + `heartbeat.md` |
| Working files on disk | `context/memory/YYYY-MM-DD.md` session logs (L2) — written automatically, loaded on demand |
| Permanent storage on disk | `context/memory.md` (L3) — curated facts, loaded via `@import` |
| System registry | `context/os-state.json` |
| System event log | `context/events.jsonl` |
| Mutex / process lock | `context/.locks/` + `kernel.py` |
| Swap / overflow | `context/memory/archive/` — old memory rotated out when L3 gets too large |
| Antivirus / endpoint protection | `PreToolUse` hooks — intercept every tool call before execution, block dangerous operations, flag anomalous patterns |
| Kernel security module (LSM / SELinux) | Hook policy files — declarative rules defining what each agent is permitted to do; violations blocked at the intercept layer before any write occurs |
| Intrusion detection / audit log | `PostToolUse` hooks + `context/events.jsonl` — every tool result is observable; `os-health-check` scans for deviation patterns |
| Task Manager | `os-health-check` agent |
| Self-updating software | `os-learning-loop` + `skill-improvement-eval` |
| **No OS equivalent** | **Self-improvement loop** — `os-learning-loop` mines `events.jsonl` for friction after every session and patches `CLAUDE.md`, `SKILL.md` files, and agent instructions. The OS rewrites its own rules based on how it was used. |
| Install new software from a store / package manager | **Generate new software on demand** — if no skill exists for what you need, ask the OS to create one. `create-skill` scaffolds a fully functional, documented skill from a plain-language description in seconds. No app store, no waiting, no existing package required. |
| **No OS equivalent** | **The LLM reasoning engine** — a traditional OS executes deterministic instructions. The Agentic OS has a language model at its core: it understands intent, interprets ambiguous instructions, synthesizes knowledge across domains, generates new code and documentation, and makes judgment calls. Every agent, skill, and hook is ultimately orchestrated by a model that can reason, not just execute. This is the fundamental architectural departure — the CPU follows instructions; the LLM understands them. |

> **Key differentiator from a traditional OS:** A conventional operating system is a static artifact — Windows does not rewrite its own kernel based on how you used it today. The Agentic OS does. Every session, `os-learning-loop` observes failures, repeated friction, and patterns in the event log, then proposes and applies patches to the system's own skill instructions and `CLAUDE.md`. Using a **Karpathy-style research loop**, `skill-improvement-eval` validates each proposed change with the `eval_runner` trainer before it is committed. Over time, the OS becomes measurably better at the specific workflows of the project it lives in. This is closer to a **living organism** than a conventional operating system — it adapts to its environment rather than remaining fixed.
>
> **A glimpse of the agentic future:** This pattern may preview how all operating systems eventually work. In an AI-native world, every user of an OS is also an implicit contributor to its improvement — agents running across millions of sessions observe friction, propose fixes, and collectively evolve the system. The Agentic OS implements this at the project scale today: a single team's usage continuously tunes the environment to their specific workflows. At planetary scale, this becomes a distributed, always-improving OS shaped by the aggregate intelligence of every agent that has ever run on it.
>
> **On-demand software creation:** On a traditional OS, if the application you need does not exist, you wait — for a vendor to build it, for an open-source maintainer to publish it, or for a developer to write it. On an Agentic OS, you describe what you need in plain language and the OS generates it: a new `SKILL.md` with full phases, logic, trigger descriptions, and documentation, ready to run in the same session. The gap between "I need a tool" and "I have a tool" collapses from weeks to seconds. This is not just a convenience — it means the OS surface area can grow infinitely to match exactly the work being done, with no external dependency.

## Why It Matters
AI assistants natively suffer from two critical limitations when operating at scale: **Context Amnesia** and **Concurrency Collisions**. 

1. **Solving Context Amnesia**: Without scaffolding, agents forget architectural decisions, styling conventions, or workflow preferences as soon as a session ends. The Agentic OS implements a procedural memory manager with "Semantic Deduplication." It intelligently captures lessons learned, deduplicates overlapping facts, and promotes critical knowledge to a long-term memory file that is automatically bootstrapped into every new session.
2. **Solving Concurrency Collisions**: When multiple agents run in parallel (or a background loop runs while a user interacts with the foreground), they can overwrite the same files, causing fatal git conflicts or file corruption. The Agentic OS implements **Strict Spinlocks** with jittered backoffs. Before an agent can write to memory or change the system state, it must acquire a file-system-level lock via the Kernel.

Together, these mechanisms upgrade a project from a "chat interface" into a resilient, fail-closed, context-aware machine.

## How and When to Use It

**When to Use It:**
You should deploy the Agentic OS into any project where an AI agent will be doing continuous, non-trivial work over multiple sessions. This includes:
* **Software Development**: To persist build commands, test patterns, and architectural decisions.
* **Research & Writing**: To maintain a long-term glossary of terms, brand voice (`soul.md`), and accumulating research logs.
* **Autonomous Workflows**: When using `/loop` or scheduled background agents to summarize logs, parse legacy systems, or audit code while you sleep.

**How to Use It:**
When integrating the Agentic OS into a new or existing repository, follow these steps:

1. **Install the Plugin**: Add the plugin to your agent's ecosystem.
2. **Invoke the Orchestrator**: Ask your agent to *"set up an agentic OS"* or *"run the agentic-os-setup agent"*.
3. **The Discovery Interview**: The `agentic-os-setup` agent will interview you about the project's goals, team size, and use case.
4. **Scaffolding**: Based on the interview, the OS will synthesize and provision the environment—generating the Kernel, `.gitignore` policies, memory folders, and state files.
5. **Daily Usage**: Throughout your work, you can explicitly command *"update memory with what we learned today"* or *"run a health check"*. The OS will also run background tasks (like the `os-learning-loop`) to autonomously observe failures and patch the system's own `CLAUDE.md` or skills to prevent future mistakes.

By treating the project repository as an Operating System, the Agentic OS ensures that the AI environment grows securely, systematically, and intelligently over the entire lifecycle of the project.
