---
concept: exploration-handoff-interactive-co-authoring
source: plugin-code
source_file: exploration-cycle-plugin/skills/exploration-handoff/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.984943+00:00
cluster: session
content_hash: 8b10345bccfac5bf
---

# Exploration Handoff (Interactive Co-Authoring)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: exploration-handoff
description: >
  Interactive co-authoring skill for the narrow end of the exploration funnel.
  Synthesizes session briefs, BRDs, story sets, and prototype notes into a
  structured handoff package targeted at the correct downstream consumer
  (e.g., formal software specs, strategic roadmaps, or process documentation).
allowed-tools: Bash, Read, Write
---

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
<commentary>User has finished exploration and wants to produce a handoff package.</commentary>
User: I finished my exploration session, help me write the handoff package.
Agent: [invokes exploration-handoff, synthesizes session artifacts into structured handoff]
</example>

<example>
<commentary>User wants to synthesize all exploration artifacts for a specific downstream consumer.</commentary>
User: Synthesize our session captures into a handoff for the engineering team.
Agent: [invokes exploration-handoff, targets handoff at engineering/spec downstream]
</example>

<example>
<commentary>Starting a new session routes to exploration-session-brief, not this skill.</commentary>
User: Let's kick off a new exploration session.
Agent: [invokes exploration-session-brief, NOT exploration-handoff]
</example>

# Exploration Handoff (Interactive Co-Authoring)

> **Note:** This skill runs fully interactively via Claude — no script needed. `execute.py` is a planned batch-mode convenience wrapper that hasn't been built yet, but the core skill works now. The [handoff-preparer-agent](../../agents/handoff-preparer-agent.md) provides an alternative agentic dispatch path.

## When This Phase Is Required vs Optional

- **Greenfield (Type 1):** Always required — the handoff package is how the engineering team knows what to build.
- **Brownfield (Type 2):** Optional — if the same person/agent is doing both exploration and implementation, formal handoff may be unnecessary. The SME decides during session setup.
- **Analysis/Docs (Type 3):** Always required — the handoff IS the primary output of the session (requirements, process maps, analysis reports, stories, rules, workflow diagrams, or whatever the non-software deliverable is).
- **Spike (Type 4):** Optional — depends on whether findings need to be communicated to others.

If this phase was skipped during session setup, it will be marked `- [~]` in the dashboard and the orchestrator will not route here.

This skill provides a structured, 3-stage interactive workflow for synthesizing exploration artifacts into a concise Handoff Package.

**Important Note for Agents:** Do NOT passively run a bash script or dump a massive block of markdown. You must guide the user through the following 3 stages.

## Stage 0: Scribe Activities (Automated Capture Before Synthesis)

First, read the dashboard `**Session Type:**` field. This determines what Stage 0 does.

**Non-software sessions** (session type contains "process", "strategic", "risk/compliance", or "legacy analysis"):
- Skip prototype-related captures.
- Check whether `exploration/captures/` contains any of: problem-framing.md, brd-draft.md, workflow-diagram.md.
- If captures are missing, announce: *"Before I package the hand

*(content truncated)*

## See Also

- [[domain-patterns-exploration-cycle]]
- [[domain-patterns-exploration-session-failures]]
- [[exploration-cycle-plugin-hooks]]
- [[exploration-workflow-sme-orchestrator]]
- [[pre-parse-for---headless-to-set-non-interactive-backend-before-pyplot-import]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/skills/exploration-handoff/SKILL.md`
- **Indexed:** 2026-04-27T05:21:03.984943+00:00
