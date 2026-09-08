---
name: os-guide
plugin: agent-agentic-os
description: >
  Trigger with "explain agentic os", "how do I set up a persistent agent environment",
  "what is the CLAUDE.md hierarchy", "explain the context folder structure",
  "how does session memory work", "what is soul.md or user.md", "explain auto-memory or MEMORY.md",
  "what is a loop scheduler or heartbeat", or when the user asks for the canonical guide.
allowed-tools: Read, Write
---

# Agentic OS Guide

The core insight: LLMs are stateless functions. `CLAUDE.md` is the only file loaded by
default into every conversation. The **Agentic OS** pattern turns this constraint into a
full operating system metaphor (kernel = CLAUDE.md hierarchy, RAM = context/ folder, disk =
dated session logs, stdlib = skills/, processes = sub-agents, shell = slash commands, cron =
/loop, boot = START_HERE.md, autoresearch loop = os-eval-runner). Full OS-concept mapping and
the skill-category table (orchestration/evaluation/mutation/memory/reporting/bootstrap/
utility/diagnostic) are in `references/detailed-reference.md`. Dependencies (Python 3.8+,
stdlib only) are also there.

## Execution Flow

Execute these phases in order. Do not skip phases. This skill uses **Progressive Disclosure**. Load only what you need:

1. For CLAUDE.md scope rules and precedence -> read `references/architecture/claude-md-hierarchy.md`
2. For context/ folder patterns (soul.md, user.md, memory.md) -> read `references/architecture/context-folder-patterns.md`
3. For /loop and heartbeat.md scheduling -> read `references/operations/loop-scheduler.md`
4. For sub-agents, hooks, auto-memory -> read `references/architecture/sub-agents-and-hooks.md`
5. For memory hygiene (write/promote/archive rules) -> read `references/memory/memory-hygiene.md`
6. For the full canonical directory tree -> read `references/architecture/canonical-file-structure.md`
7. For the self-improving OS Triple-Loop and 3-file autoresearch framework -> read `references/research/optimizer-engine-patterns.md` and `references/research/karpathy-autoresearch-3-file-eval.md`

Quick orientation (Anthropic-native vs. community-layered conventions) and the Design Principle
("every line in CLAUDE.md competes for attention — keep it under 300 lines") are in
`references/detailed-reference.md`.

## Discovery: What Does the User Need?

Ask the user which aspect they need help with:

1. **Setting up** a new Agentic OS from scratch -> read `references/architecture/canonical-file-structure.md`, walk them through the setup
2. **Understanding** a specific layer (context/, hooks, /loop) -> load the matching reference file
3. **Memory management** (what to record, promote, archive) -> invoke `os-memory-manager` skill
4. **Continuous Improvement** (retrospectives, skill updates) -> invoke `Triple-Loop Retrospective` agent
5. **Troubleshooting** (context not loading, skills not triggering) -> read `references/architecture/claude-md-hierarchy.md` for scope precedence

## The Improvement Triple-Loop (Mandatory Close Protocol)

Every significant work session — especially eval runs, skill edits, backports, and agent
loop completions — must close through this two-phase protocol. **Do not consider a session
complete without running both phases.**

> **Session Lifecycle Invariant**: The OUTER loop (`os-improvement-loop`) owns session
> lifecycle. INNER loops (`os-eval-runner`) never close a session. A session is incomplete
> until Phase 6 is executed. `Triple-Loop Retrospective` (agent) detects friction and
> identifies targets; `os-improvement-loop` (skill) is the execution protocol once a target
> is identified.

```
Work → Backport/Ship → Phase 6: Capture → Phase 7: Improve
```

**Phase 6: Capture Learnings** — after any backport, eval run, or skill change, invoke
`os-memory-manager` to write a dated session log and promote non-obvious findings (snags,
footguns, architectural decisions, ADAPT patterns — skip routine score improvements). Full
template and write locations are in `references/detailed-reference.md`.

**Phase 7: Continuous Improvement** — when routing accuracy reveals a weak skill, invoke
`os-improvement-loop` with the target skill and a locked eval set; it runs mutate→eval→
KEEP/DISCARD cycles until improvement is confirmed, then `os-eval-backport` gates the winner
to production. See [os-improvement-loop SKILL.md](../os-improvement-loop/SKILL.md).

The full 5-step Triple-Loop diagram is in `references/detailed-reference.md`. Skipping Phase 6
or 7 means knowledge evaporates at session end and skill quality drifts.

## Next Actions

- For memory write/promote/archive decisions -> invoke `os-memory-manager`
- To orchestrate an end-to-end setup of a new environment -> run `agentic-os-setup`
- To perform a retrospective and improve the OS -> run `Triple-Loop Retrospective`
- To add a scheduled heartbeat -> read `references/operations/loop-scheduler.md`

## Mandatory Close: Friction Signal (Every Invocation)

After answering the user's question, emit a friction event for anything that was unclear,
missing from the references, or required more turns than expected to explain:

```bash
# Only emit if friction was encountered — do not emit if explanation was clean
python context/kernel.py emit_event --agent os-guide \
  --type friction --action encountered \
  --summary "step:[which-reference] cause:[what-was-unclear]"
```

Then answer: **What one addition to the guide references would have made this explanation
clearer or faster?** Record the answer as a comment in the next session log or flag it
to `Triple-Loop Retrospective` if the same gap appears across multiple sessions.
