---
name: agentic-os-guide
description: >
  Trigger with "explain agentic os", "how do I set up a persistent agent environment", 
  "what is the CLAUDE.md hierarchy", "explain the context folder structure", 
  "how does session memory work", "what is soul.md or user.md", "explain auto-memory or MEMORY.md", 
  "what is a loop scheduler or heartbeat", or when the user asks for the canonical 
  reference and operational guide for the Agentic OS / Agent Harness pattern.
disable-model-invocation: false
allowed-tools: Read, Write
---
# Agentic OS Guide

The core insight: LLMs are stateless functions. `CLAUDE.md` is the only file loaded by
default into every conversation. The **Agentic OS** pattern turns this constraint into a
full operating system metaphor.

| OS Concept | Agent Equivalent |
|------------|-----------------|
| Kernel | `CLAUDE.md` hierarchy (global -> org -> project -> local) |
| RAM | `context/` folder (soul, user prefs, memory) |
| Disk | `context/memory/YYYY-MM-DD.md` dated session logs |
| Stdlib | `skills/` procedural knowledge bundles |
| Processes | `.claude/agents/` sub-agents with isolated context |
| Shell | `.claude/commands/` slash commands |
| Cron | `/loop` + `heartbeat.md` scheduled background tasks |
| Boot | `START_HERE.md` + `MEMORY.md` bootstrap on session start |

## Execution Flow

Execute these phases in order. Do not skip phases. This skill uses **Progressive Disclosure**. Load only what you need:

1. For CLAUDE.md scope rules and precedence -> read `references/claude-md-hierarchy.md`
2. For context/ folder patterns (soul.md, user.md, memory.md) -> read `references/context-folder-patterns.md`
3. For /loop and heartbeat.md scheduling -> read `references/loop-scheduler.md`
4. For sub-agents, hooks, auto-memory -> read `references/sub-agents-and-hooks.md`
5. For memory hygiene (write/promote/archive rules) -> read `references/memory-hygiene.md`
6. For the full canonical directory tree -> read `references/canonical-file-structure.md`

## Quick Orientation

### Anthropic-Native vs Community-Layered

**What Anthropic ships natively:**
- CLAUDE.md layered discovery (global, org, project, local, subdirectory scopes - most specific wins)
- Auto-memory (`MEMORY.md`) - Claude writes this itself with build commands, style prefs, architecture decisions
- `/loop` command for cron-style scheduling (up to 50 tasks per session, auto-expire after 3 days)
- Agent Skills: `SKILL.md`-based procedural knowledge bundles
- Sub-agents in `.claude/agents/` with isolated tool contexts

**What the community layered on top:**
- `context/soul.md`, `context/user.md`, `context/memory/{date}.md` folder conventions
- `START_HERE.md` bootstrap prompt pattern
- Lessons-learned -> update-skills-after-session loop
- `heartbeat.md` scheduled task definition files

## Design Principle

> Every line in `CLAUDE.md` competes for attention with actual work.
> Keep it under 300 lines. Focus on what Claude would get wrong without it.
> Use `@import context/soul.md` to load identity on demand, not always.

## Discovery: What Does the User Need?

Ask the user which aspect they need help with:

1. **Setting up** a new Agentic OS from scratch -> read `references/canonical-file-structure.md`, walk them through the setup
2. **Understanding** a specific layer (context/, hooks, /loop) -> load the matching reference file
3. **Memory management** (what to record, promote, archive) -> invoke `session-memory-manager` skill
4. **Continuous Improvement** (retrospectives, skill updates) -> invoke `os-learning-loop` agent
5. **Troubleshooting** (context not loading, skills not triggering) -> read `references/claude-md-hierarchy.md` for scope precedence

## Next Actions

- For memory write/promote/archive decisions -> invoke `session-memory-manager`
- To orchestrate an end-to-end setup of a new environment -> run `agentic-os-setup`
- To perform a retrospective and improve the OS -> run `os-learning-loop`
- To add a scheduled heartbeat -> read `references/loop-scheduler.md`
