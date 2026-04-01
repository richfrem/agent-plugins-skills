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

1. **Outline First:** Propose a numbered list of items that *must* be communicated to this specific audience. For each item, state whether it is a confirmed decision, a constraint, or an open question. Ask the user: *"Does this outline reflect what we confirmed? Anything missing or wrong?"*
2. **Curate:** Apply changes. If the user promotes an `[UNCONFIRMED]` item, ask them to confirm it first before including it as fact.
3. **Draft section by section:** For each section, write a concise draft (3–6 sentences or a short list). Cite the source artifact for any major claim (e.g., "per session brief"). Ask: *"Accurate? Anything to add or cut?"* Apply edits before moving on.

## Stage 3: Reader Testing (Consumer Validation)
Ensure the handoff gives the downstream consumer what they need to act:

1. **Predict blockers:** Based on the target audience type, predict exactly 3 questions they will ask after reading this document that are NOT answered by it. Use audience-specific framing:
   - *Engineering*: implementation questions ("How should we handle X edge case?", "What's the auth strategy?")
   - *Executive/sponsor*: decision questions ("What's the fallback if this fails?", "What's the cost?")
   - *Operations*: process questions ("Who owns step 3?", "What's the escalation path?")
   - *Product/design*: scope questions ("What's explicitly out of scope?", "Which user type is primary?")

2. **Surface gaps:** Present the 3 questions: *"If [audience] reads this, they'll immediately ask: [Q1], [Q2], [Q3]. Are these answered?"*
3. **Resolve:** For each unanswered question, ask whether to (a) answer it inline, (b) add it to `## Unresolved Ambiguity` for the execution phase to own, or (c) confirm it's intentionally out of scope.

## Anti-Hallucination Rules
- Do NOT invent requirements or rules that were not present in the Stage 1 input sources.
- Maintain traceability: When stating a major constraint or rule, briefly mention which exploration source it came from.
- Be explicitly clear about what is a confirmed decision versus what is an optimistic assumption.

## Final Output Destination
Write the approved markdown content to: `exploration/handoffs/handoff-package.md` (or a timestamped equivalent).
