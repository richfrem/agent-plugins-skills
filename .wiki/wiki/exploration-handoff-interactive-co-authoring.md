---
concept: exploration-handoff-interactive-co-authoring
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/exploration-handoff/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.076996+00:00
cluster: plugin-code
content_hash: ac8d66872335d025
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

This skill provides a structured, 3-stage interactive workflow for synthesizing exploration artifacts into a concise Handoff Package.

**Important Note for Agents:** Do NOT passively run a bash script or dump a massive block of markdown. You must guide the user through the following 3 stages.

## Stage 1: Context Gathering (Routing)
Before synthesizing anything, establish what you're working with and where it's going. Ask both questions in a single message:

1. **Target audience:** Who receives this handoff and what will they do with it?
   - *Engineering team* — writing a formal spec or implementation plan
   - *Executive or sponsor* — making a go/no-go or budget decision
   - *Operations or process team* — updating a workflow or policy
   - *Product or design team* — scoping a discovery sprint or prototype
   - *Other* — describe briefly

2. **Available artifacts:** Which exploration documents exist? (Check `exploration/` directory — list what you find.) Common sources: session brief, BRD draft, prototype notes, user story set, business-workflow diagrams.

After the user responds: read each artifact file they identify. If a file doesn't exist, note it explicitly and ask whether to proceed without it or pause until it's available. Do not invent content for missing artifacts.

## Stage 1.5: Risk & Rigor Assessment
Before synthesis, perform a mandatory risk assessment to determine the "Rigor Tier" for the downstream execution phase:

- **Tier 1 (Low Risk)**: Internal R&D, limited data. Lightweight, self-assessed development cycle.
- **Tier 2 (Moderate Risk)**: Internal data, standard tools. Requires security team review, mandatory red teaming, and context sanitization.
- **Tier 3 (High Risk)**: PII/Sensitive data, high-privilege tools (Bash). Mandatory full `spec-kitty` engineering cycle with architectural hardening (e.g., **Countermind** SBL, **Pro2Guard** sidecar enforcement).

Ask the user to categorize the project based on these tiers and document the result in the handoff package.

## Stage 2: Synthesis and Iterative Refinement
Your job is to extract the signal relevant to the target audience — not to copy-paste source documents.

**Signal** = confirmed decisions, hard constraints, and questions that block the next phase.
**Noise** = background context, rationale already obvious to the audience, and anything marked `[UNCONFIRMED]` in source documents.

1. **Outline First:** Propose

*(content truncated)*

## See Also

- [[exploration-session-brief-interactive-co-authoring]]
- [[exploration-session-brief-interactive-co-authoring]]
- [[prototype-builder-interactive-co-authoring]]
- [[acceptance-criteria-exploration-handoff]]
- [[acceptance-criteria-exploration-handoff]]
- [[exploration-cycle-plugin-handoff-preparer-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/exploration-handoff/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.076996+00:00
