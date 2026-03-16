# Agentic OS: Executive Summary

## What is the Agentic OS Plugin?
The **Agentic OS** plugin is a foundational scaffolding framework that transforms a standard project repository into a persistent, multi-agent environment. It bridges the gap between ephemeral conversational AI sessions and long-term, autonomous agent operations (such as those performed by Claude Code or GitHub Copilot CLI). 

Using a traditional Operating System metaphor, the plugin scaffolds a robust architecture directly into the host project:
* **The Kernel (`CLAUDE.md` & `context/kernel.py`)**: Acts as the central nervous system, managing atomic file locks, system state, and event routing.
* **RAM & Storage (`context/`)**: Manages tiered memory consisting of L1 cache (`os-state.json`, `events.jsonl`), L2 session logs, and L3 long-term semantic memory (`memory.md`).
* **Standard Library (`skills/`)**: Provides tools to manage memory formatting, clean stale locks, and initialize environments.
* **Background Processes (`agents/`)**: Specialized sub-agents like the `os-learning-loop` (for continuous improvement), `os-health-check` (for system metrics), and `session-memory-manager` (for deduplicating and promoting facts).

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
