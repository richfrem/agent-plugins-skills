---
concept: skill
source: plugin-code
source_file: exploration-cycle-plugin/skills/subagent-driven-prototyping/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.989912+00:00
cluster: component
content_hash: a399ab25866ceb7f
---

# Skill

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/exploration-cycle-plugin/skills/subagent-driven-prototyping/SKILL.md -->
---
name: subagent-driven-prototyping
description: >
  Builds a prototype component by component, self-reviewing each component against the Discovery Plan before moving to the next. Invoked by prototype-builder after the layout direction is confirmed. Trigger phrases: "build the prototype", "let's build it", "start building". Also invoked by prototype-builder-agent after visual-companion confirms layout.
allowed-tools: Bash, Read, Write
---

> Architectural patterns adapted from [obra/superpowers](https://github.com/obra/superpowers) (MIT)

## Dashboard Intercept

Before doing anything else, silently check for `exploration/exploration-dashboard.md`.

- **If the file EXISTS:** Read it silently and check the `**Status:**` line.
  - If `**Status:** Complete` → the prior session has ended. Proceed with this skill's
    standalone flow as normal.
  - Otherwise → an active session is in progress. Stop immediately. Do not continue here.
    Announce to the user:
    > "It looks like you have an active Exploration Session in progress. Let me take you back
    > to your session dashboard so we can keep your progress on track."
    **Return to the orchestrator.** Use the Skill tool: `skill: "exploration-workflow"`.
    After invoking it, stop generating output from this skill — do not continue below.

- **If the file does NOT exist:** Proceed with this skill's standalone flow as normal.

<example>
<commentary>Demonstrates the skill being invoked by prototype-builder after layout has been confirmed by visual-companion.</commentary>
User: [dispatched by prototype-builder after layout confirmed]
Agent: Verifies the Discovery Plan and layout direction files exist, announces the number of components and their plain-language names, then builds each one in order — announcing each start, checking it against the plan on completion, and reporting each as done before moving to the next.
</example>

<example>
<commentary>Demonstrates a user triggering the skill directly after plan approval.</commentary>
User: Let's build it
Agent: Checks for the required Discovery Plan and layout direction files. If both exist, announces the build plan in plain language and begins building each component one at a time with progress updates.
</example>

## Orchestrator Context

If dispatched by `exploration-workflow`, the Discovery Plan and layout direction have
already been approved by the SME. The Required Inputs Check below is a verification
step only — do not re-present these artifacts for re-approval. Proceed directly to
Component Decomposition once inputs are confirmed present.

## Execution Discipline (powered by orba/superpowers)

> **Required:** The `orba/superpowers` plugin must be installed.

This skill invokes superpowers execution discipline skills during the build loop.

### Isolation
Before building, check if a worktree/feature branch was set up by the orchestrator.
If not, and the session type is brownfield or greenfield, **invoke
`superpowers:using-git-worktrees`** now to create one.

### Dispatch Strategy
Read the `**Dispatch Strategy:**` field from the dashboard. Use it to determine how to
dispatch component implementation:

- **`copilot-cli`:** Use `copilot-cli-agent` skill. Simple components → `gpt-5-mini` (free).
  Complex/multi-file components → `claude-sonnet-4-6` (batch into one dense request —
  charged per request, not per token).
- **`claude-subagents`:** Use the `Agent` tool. Mechanical components → `model: "haiku"`.
  Complex components → `model: "sonnet"`.
- **`direct`:** Build each component directly in this session.

### Two-Stage Review (per component)
After each component is built, **invoke `superpowers:requesting-code-review`** twice:
1. **Plan alignment check** — reviewer sub-agent verifies component matches the Discovery Plan
2. **Quality check** — reviewer sub-agent checks code quality and codebase conventions

For `copilot-cli` and `claude-subagents` dispatch: use a separate sub-agent for each review.
For `direct` mode: self-r

*(content truncated)*

<!-- Source: plugin-code/agent-agentic-os/skills/os-architect/SKILL.md -->
---
name: os-architect
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
in `agen

*(combined content truncated)*

## See Also

- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[check-all-text-files-in-skill-for-regex-py-mentions]]
- [[for-a-skill]]
- [[only-process-plugin-root-level-files-not-skill-files]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/skills/subagent-driven-prototyping/SKILL.md`
- **Indexed:** 2026-04-27T05:21:03.989912+00:00
