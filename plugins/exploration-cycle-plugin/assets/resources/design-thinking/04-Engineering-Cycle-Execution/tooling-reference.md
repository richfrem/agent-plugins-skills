# Opportunity 4: Tooling Reference

A reference guide to the three-layer stack used in Opportunity 4 execution. Each tool is linked to its source and described in terms of what it contributes to the pipeline.

---

## Layer 1 — Spec-Kits (Specification Driven Design)

These frameworks define *what gets built* and enforce the structure and constraints the engineering agent must follow. They translate human-validated intent into machine-consumable specifications that serve as the agent's contract.

---

### GitHub Spec-Kit
**[github/spec-kit](https://github.com/github/spec-kit)** · Open source · 72,000+ GitHub stars

GitHub's official open-source toolkit for spec-driven development. Provides templates and workflows for the full specify → plan → tasks → implement cycle. Supports over 22 AI agent platforms out of the box including Claude Code, GitHub Copilot, Amazon Q, and Gemini CLI. Cross-platform (shell scripts for Unix, PowerShell for Windows).

The most widely adopted SDD framework in the ecosystem. A good starting point for teams new to spec-driven development before introducing more opinionated tooling.

**Best for:** Teams wanting broad platform support and a low-friction entry point into SDD with minimal setup.

---

### Spec-Kitty
**[Priivacy-ai/spec-kitty](https://github.com/Priivacy-ai/spec-kitty)** · Open source · `pip install spec-kitty-cli`

A CLI-first workflow for spec-driven development built for serious agentic execution. Takes the spec → plan → tasks → implement → review → merge lifecycle and enforces it with repository-native artifacts, a live Kanban dashboard, git worktree isolation per feature, and automated merge workflows.

Key distinction from Spec-Kit: Spec-Kitty is opinionated and enforcing. It maintains a live `implementation_plan.md` that tracks progress in real time, uses `.clinerules` to set strict agent boundary constraints, and exposes an orchestrator API (`spec-kitty orchestrator-api`) for multi-agent coordination. The dashboard auto-starts and shows which agents are working on which work packages.

Current stable release is the 3.x line. Integrates directly with Claude Code, Cursor, Gemini, and Codex.

**Best for:** Teams running parallel agentic work across multiple features, needing strong boundary enforcement and auditability.

---

### OpenSpec
**[Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)** · Open source · Stable as of January 2026

A lightweight spec layer that adds structure to the agreement between human and agent before any code is written. Each change gets its own folder containing a proposal, specs, design document, and tasks — allowing fluid iteration without rigid phase gates.

Designed to be tool-agnostic: supports 20+ AI coding tools including Claude, Cursor, Cline, Codex, GitHub Copilot, Kiro, and Windsurf. Entry point is `/opsx:propose "your idea"` which creates the full proposal scaffold.

The explicit goal is eliminating "vibe coding" — unstructured natural language conversations where requirements scatter across chat logs with no persistence or systematization.

**Best for:** Teams wanting a lightweight, tool-agnostic spec layer that doesn't impose a heavy workflow overhead.

---

### BMAD-Method
**[bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)** · Open source · [docs.bmad-method.org](https://docs.bmad-method.org)

Breakthrough Method for Agile AI-Driven Development. A multi-agent framework where specialized AI agents — each defined by a self-contained Markdown persona file — handle distinct roles across the full development lifecycle: Analyst, Product Manager, Architect, Scrum Master, Product Owner, Developer, and QA.

The key architectural distinction: every agent produces a verifiable artifact (PRD, architecture diagram, test plan, sprint stories), not just a chat response. These persistent documents can be reviewed, versioned, and handed off between agents as structured work products. Current release is v6 Alpha, with a Scale Adaptive Framework that moves fluidly from solo prototype to team and enterprise scale without requiring a methodology rewrite.

**Best for:** Complex greenfield builds where different aspects of the work benefit from clearly separated agent roles, each operating against its own bounded context.

---

## Layer 2 — Agentic Frameworks (Cognitive & Orchestration)

These SDKs determine *how the engineering agent thinks and coordinates*. They provide the reasoning, tool-use, and multi-agent orchestration capabilities that the engineering agent runs on top of the spec layer above.

---

### Claude Agent SDK
**[Anthropic](https://platform.claude.com/docs/en/agent-sdk/overview)** · [anthropic.com/engineering/building-agents-with-the-claude-agent-sdk](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)

Formerly the Claude Code SDK, renamed in late 2025 to reflect its role as a general-purpose agent runtime. Provides the same tools, agent loop, and context management that power Claude Code — file reading, command execution, web search, code editing — exposed as a programmable SDK.

Supports subagents natively, enabling parallelisation where multiple subagents work on different tasks with isolated context windows. Has the deepest MCP (Model Context Protocol) integration in the ecosystem, connecting agents to tools and data sources via JSON-RPC. Primary orchestration layer for Claude-based engineering agents in this pipeline.

**Best for:** Claude-first engineering agents requiring deep MCP integration and native subagent support.

---

### Microsoft Agent Framework
**[Microsoft Learn](https://learn.microsoft.com/en-us/agent-framework/)** · [devblogs.microsoft.com](https://devblogs.microsoft.com/semantic-kernel/build-ai-agents-with-claude-agent-sdk-and-microsoft-agent-framework/)

Microsoft's agentic orchestration framework, built on Semantic Kernel. Enables multi-agent workflows that compose Claude agents alongside Azure OpenAI, OpenAI, and GitHub Copilot agents in sequential, concurrent, handoff, and group chat patterns using built-in orchestrators.

Treats Claude as one building block in a larger agentic system rather than a standalone tool. Relevant for deployments in Azure-hosted environments or organisations standardised on Microsoft's toolchain, where engineering agents need to interoperate with non-Claude agents in the same workflow.

**Best for:** Azure-hosted deployments and organisations needing Claude to interoperate with other Microsoft-ecosystem agents.

---

## Layer 3 — Agentic Harnesses (Execution & Safety Wrappers)

These tools control *how code is safely generated, tested, and delivered*. They exist specifically to prevent unverified or broken code from reaching the main repository and to keep long-running agentic sessions on track.

---

### obra/superpowers
**[obra/superpowers](https://github.com/obra/superpowers)** · Open source · Claude Code plugin

A composable skills-based execution harness for Claude Code. Provides a zero-dependency framework of skills and initial instructions that keep the agent using a structured software development workflow rather than jumping directly into writing code.

Key behaviour: when given a new task, the agent steps back, teases out a spec through conversation, confirms it in readable chunks, then executes against it. Not uncommon for the agent to work autonomously for hours without deviating from the agreed plan. Installable directly via the Claude Code plugin marketplace:
```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

Uses an agentic harness architecture where an initiator agent sets up the file system, project structure, and task breakdown, and coding sub-agents work on small parts while checkpointing progress between context windows.

**Best for:** Claude Code-based workflows needing a structured, skill-driven execution harness that enforces spec-first behaviour without heavy tooling overhead.

---

### GSD — Get Shit Done
**[gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done)** · Open source · 11,900+ GitHub stars · [gsd.build](https://gsd.build)

A meta-prompting, context engineering, and spec-driven development system designed to prevent context rot in long agentic sessions. Originally a viral prompt framework for Claude Code; the current v2 is a full standalone CLI built on the Pi SDK with direct TypeScript access to the agent harness itself.

What GSD v2 can do that prompt-based approaches cannot: clear context between tasks precisely, inject exactly the right files at dispatch time, manage git branches, track cost and token usage, detect stuck loops, recover from crashes, and auto-advance through an entire milestone without human intervention.

Orchestrates ephemeral sub-agents (Researchers, Planners, Executors, Checkers) each with strictly isolated, fresh context windows. Every micro-task fires an atomic git commit with a hash and updates a `SUMMARY.md`, so if a feature breaks you know exactly which 15-minute chunk introduced the bug. Multi-provider: Anthropic, OpenAI, Google Gemini, OpenRouter, GitHub Copilot, Amazon Bedrock, and 15+ more.

Trusted by engineers at Amazon, Google, and Shopify. Antigravity-compatible version available at [toonight/get-shit-done-for-antigravity](https://github.com/toonight/get-shit-done-for-antigravity).

**Best for:** Long-running agentic sessions where context rot, stuck loops, and milestone tracking are the primary risks to execution quality.

---

### Execution Sandbox
Isolated containerised environment (Podman + Postgres or equivalent) where generated code is deployed and integration-tested against specs derived directly from Phase 2 and Phase 3 before any delivery to the main repository. Not a third-party tool — built and configured per deployment.

**Blast radius rule:** Code never exits the sandbox until it explicitly passes spec verification. This is non-negotiable.

---

## Tool Selection Guide

| Situation | Recommended |
|---|---|
| New to SDD, need broad platform support | GitHub Spec-Kit |
| Running parallel features with multiple agents | Spec-Kitty |
| Want lightweight, tool-agnostic spec structure | OpenSpec |
| Complex build needing role-separated agents | BMAD-Method |
| Claude-first, deep MCP integration needed | Claude Agent SDK |
| Azure-hosted or multi-vendor agent environment | Microsoft Agent Framework |
| Claude Code with structured skill-first workflow | obra/superpowers |
| Long sessions, context rot is the primary risk | GSD |
| Any production code generation | Execution Sandbox (always) |
