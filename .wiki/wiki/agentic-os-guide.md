---
concept: agentic-os-guide
source: plugin-code
source_file: agent-agentic-os/skills/os-guide/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.713413+00:00
cluster: memory
content_hash: 4f34fd90df0eeffb
---

# Agentic OS Guide

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: os-guide
description: >
  Trigger with "explain agentic os", "how do I set up a persistent agent environment", 
  "what is the CLAUDE.md hierarchy", "explain the context folder structure", 
  "how does session memory work", "what is soul.md or user.md", "explain auto-memory or MEMORY.md", 
  "what is a loop scheduler or heartbeat", or when the user asks for the canonical guide.

  

  

  
allowed-tools: Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `../../requirements.txt` for the dependency lockfile (currently empty — standard library only).

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
| Autoresearch Loop | `os-eval-runner` + `improvement-ledger.md` |

## Skill Categories (Mental Model)

| Category | Skill | One-liner |
|---|---|---|
| **Orchestration** | `os-improvement-loop` | Multi-agent concurrent loop: ORCHESTRATOR + PEER + INNER |
| **Evaluation** | `os-eval-runner` | Autoresearch eval engine — scores and gates SKILL.md iterations |
| **Evaluation** | `os-eval-lab-setup` | Bootstraps isolated lab repos for eval runs |
| **Evaluation** | `os-eval-backport` | Reviews lab results, applies approved changes to master |
| **Mutation** | `os-improvement-loop` | RED-GREEN-REFACTOR routing accuracy improvement |
| **Memory** | `os-memory-manager` | Session log writing, L2→L3 promotion, deduplication |
| **Reporting** | `os-improvement-report` | Progress charts from results.tsv + improvement ledger |
| **Bootstrap** | `os-init` | Deploys kernel.py, agents.json, Triple-Loop files to new project |
| **Utility** | `os-clean-locks` | Clears stale `.locks/` directories after agent crash |

Agents (not skills): `Triple-Loop Retrospective` (trigger/diagnostic), `os-health-check` (liveness), `agentic-os-setup` (bootstrap interview)

## Execution Flow

Execute these phases in order. Do not skip phases. This skill uses **Progressive Disclosure**. Load only what you need:

1. For CLAUDE.md scope rules and precedence -> read `references/architecture/claude-md-hierarchy.md`
2. For context/ folder patterns (soul.md, user.md, memory.md) -> read `references/architecture/context-folder-patterns.md`
3. For /loop and heartbeat.md scheduling -> read `references/operations/loop-scheduler.md`
4. For sub-agents, hooks, auto-memory -> read `references/architecture/sub-agents-and-hooks.md`
5. For memory hygiene (write/promote/archive rules) -> read `references/memory/memory-hygiene.md`
6. For the full canonical directory tree -> read `references/architecture/canonical-file-structure.md`
7. For the self-improving OS Triple-Loop and 3-file autoresearch framework -> read `references/research/optimizer-engine-patterns.md` and `references/research/karpathy-autoresearch-3-file-eval.md`

## Quick Orientation

### Anthropic-Native vs Community-Layered

**What Anthropic ships natively:**
- CLAUDE.md layered discovery (global, org, project, local, subdirectory scopes - most specific wins)
- Auto-memory (`MEMORY.md`) - Claude writes this itself with build commands, style prefs, architecture decisions
- `/loop` command for cron-

*(content truncated)*

## See Also

- [[agentic-os-operational-guide-usage]]
- [[agent-agentic-os-hooks]]
- [[after-os-evolution-verifier-run]]
- [[os-architect-test-report-scenario-id]]
- [[os-state-json]]
- [[quick-start-zero-context-guide]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/skills/os-guide/SKILL.md`
- **Indexed:** 2026-04-27T05:21:03.713413+00:00
