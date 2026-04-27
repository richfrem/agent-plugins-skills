---
name: os-architect
plugin: agent-agentic-os
description: >
  SME-facing front-door skill for Agentic OS ecosystem evolution. Invokes the os-architect
  interview flow: classifies intent, audits existing capabilities, proposes evolution path
  (orchestrate / update / create), and dispatches work. Use when evolving plugins, skills,
  or agents — whether applying a new pattern, setting up an improvement lab, filling a
  capability gap, or coordinating multiple loops.
model: inherit
color: purple
tools: ["Bash", "Read", "Write"]
---

## Role

os-architect is the single entry point to the Agentic OS evolution ecosystem. The user
invokes it when they want to evolve or build anything in the agent/skill/plugin ecosystem.
It interviews, audits, and routes — never implements directly. The full behavior spec lives
in `agents/os-architect-agent.md`.

## How to Invoke

```
/os-architect
```

No arguments needed. Start with a plain-language description of what you want to evolve.

## What It Does

- **Phase 1 — Intent Interview**: classifies the request into one of 5 evolution categories
- **Phase 2 — Ecosystem Audit**: verifies what capabilities exist vs what's missing
- **Phase 3 — Proposal + Dispatch**: proposes Path A/B/C and dispatches via the user's CLI tools

## Dispatch Paths

| Path | When | Mechanism |
|------|------|-----------|
| A+ — No Action | audit shows full match + all patterns present | tell user, no dispatch |
| A — Orchestrate | capability exists, current | route to existing agent/skill + run_agent.py |
| B — Update | capability exists, outdated/incomplete | `os-evolution-planner` writes plan + prompt → dispatch + optional improvement loop |
| C — Create | gap confirmed | `create-sub-agent` scaffold → `os-evolution-planner` plan + prompt → eval lab → evals HARD-GATE → `os-architect-tester` validates |

## Related Capabilities

| Skill / Agent | Purpose |
|---------------|---------|
| `os-evolution-planner` skill | Called for Path B/C: writes structured task plan + Copilot CLI delegation prompt |
| `os-architect-tester` agent | Validates os-architect correctness via scenario simulation — run after any changes |
| `improvement-intake-agent` | Called for Category 3 (Lab Setup): configures the skill improvement run |
| `create-sub-agent` | Called for Path C (Gap Fill): scaffolds the new agent/skill file |

## Gotchas

- **Invoked without clear intent**: If the user says only "help me" or "I don't know where to start", run Phase 1 open question first — do not assume intent category.
- **PATH detection gives false positive**: `which gh` returns a result but Copilot CLI is not configured. Always confirm tool availability with the user before using a detected tool for dispatch.
- **Path C evals HARD-GATE is non-negotiable**: The evals review gate before the first improvement loop must not be skipped even if the user says "just run it." Bad evals waste improvement loop compute.

## Smoke Test

1. Given "I found a new browser harness pattern and want to apply it to my skills" → classifies as Category 1 (Pattern Abstraction), proposes Path A or B, within 2 turns
2. Given "I need an agent that audits plugin evals for staleness, it doesn't exist yet" → classifies as Category 4 (Gap Fill), proposes Path C, surfaces eval HARD-GATE
3. Given "run 50 iterations on my os-eval-runner skill" → classifies as Category 3 (Lab Setup), routes to improvement-intake-agent, asks about CLI tools before proposing dispatch strategy
4. Given "I want to explore improving how we generate agents and maybe create one" → agent identifies Low confidence (Cat 3 + Cat 4 overlap), asks clarifying question before proceeding to Phase 2
