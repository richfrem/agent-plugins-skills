---
name: exploration-session-brief
plugin: exploration-cycle-plugin
description: >
  Interactive co-authoring skill for the wide end of the exploration funnel.
  Captures and refines the core intent, whether the outcome is a software app,
  a business process improvement, research analysis, or strategic roadmap.
  Guides users through gathering context, iteratively drafting the brief, and
  testing for blind spots.
allowed-tools: Bash, Read, Write
---

<example>
<commentary>User wants to start a new exploration session.</commentary>
User: Let's kick off a new exploration session. I want to capture a brief for the problem I've been thinking about.
Agent: [invokes exploration-session-brief, starts Stage 1 context gathering]
</example>

<example>
<commentary>User has a vague idea and wants structured help thinking it through.</commentary>
User: I have a rough idea to explore — somewhere between a process improvement and a new feature. Can you help me think it through and write it up?
Agent: [invokes exploration-session-brief, guides user through the 3-stage co-authoring workflow]
</example>

<example>
<commentary>Explanation request — do NOT invoke. Only trigger when user actively wants to start or capture a brief, not when asking about the skill.</commentary>
User: What does the exploration-session-brief skill do? Don't start it yet.
Agent: [explains the skill without invoking it]
</example>

<example>
<commentary>Handoff requests route to exploration-handoff, not this skill.</commentary>
User: I finished my exploration session, help me write the handoff package.
Agent: [invokes exploration-handoff, NOT exploration-session-brief]
</example>

# Exploration Session Brief (Interactive Co-Authoring)

> **Note:** This skill runs fully interactively via Claude — no script needed. `execute.py` is a planned batch-mode convenience wrapper that hasn't been built yet, but the core skill works now. The [intake-agent](../../agents/intake-agent.md) provides an alternative agentic dispatch path.

This skill provides a structured, 3-stage interactive workflow for generating an Exploration Session Brief. Guide the user through each stage in sequence — do not skip ahead or dump the full brief at once.

**Important Note for Agents:** Do NOT passively run a bash script or dump a massive block of markdown. You must guide the user through the following 3 stages.

## Stage 1: Context Gathering
Your goal is to understand the boundaries of the exploration *before* drafting anything. Ask all three questions together in a single message:

1. **Domain:** What category best fits this exploration?
   - *Software feature or system* — new capability, redesign, or technical spike
   - *Business process* — workflow, approval flow, operations improvement
   - *Risk or compliance* — mitigation strategy, audit finding, policy gap
   - *Research or strategy* — market analysis, competitive review, roadmap decision
   - *Other* — describe it briefly

2. **Trigger:** What specific event, pain point, or decision caused us to start this session right now?

3. **Raw material:** Do you have any notes, transcripts, screenshots, or prior docs to share? *(You can brain-dump freely — messy is fine.)*

Wait for the user's response. If any answer is too sparse to proceed (e.g., one-word domain, no trigger explained), ask one targeted follow-up before moving to Stage 2. Do not proceed until you have a clear trigger and at least one concrete detail.

## Stage 2: Section-by-Section Refinement
Build the brief iteratively — do not write the entire document in one pass.

1. **Propose the Outline:** Based on the domain from Stage 1, propose a section list using the appropriate template below. Present it as a numbered list and ask the user: *"Does this structure fit? Anything to add or remove?"*

   | Domain | Suggested sections |
   |---|---|
   | Software feature/system | Problem Statement · Stakeholders · Current Behavior · Desired Behavior · Constraints · Open Questions |
   | Business process | Problem Statement · Stakeholders · Current Process · Pain Points · Desired State · Constraints · Open Questions |
   | Risk/compliance | Risk Description · Affected Parties · Current Exposure · Mitigation Options · Constraints · Open Questions |
   | Research/strategy | Research Question · Context · What We Know · What We Don't Know · Success Criteria · Open Questions |

2. **Curate:** Apply any changes the user requests. If they want a custom section, add it. Do not argue for the template.

3. **Draft section by section:** For each section, write a 2–5 sentence draft using only information from Stage 1. Present it and ask: *"What should we keep, cut, or change?"* Apply edits before moving to the next section. Mark anything inferred (not stated by user) as `[UNCONFIRMED]`.

## Stage 3: Reader Testing (Blind Spot Analysis)
Once all sections are drafted and approved, stress-test the brief before writing it out:

1. Pick the most likely first reader — the person who will act on this brief (e.g., an engineer building a spec, a manager approving budget, a team changing a process).
2. Predict exactly 3 questions that reader would ask after reading the brief *if they had never been part of this session*. Make the questions specific to this brief's content, not generic.
3. Present the 3 questions to the user: *"If [reader] reads this, they'll likely ask: [Q1], [Q2], [Q3]. Does the brief answer these? Should we add answers inline or list them in `## Open Questions`?"*
4. Apply whatever the user decides.

## Anti-Hallucination Rules
- Do NOT assume the output will be a software product unless the user says so. Ensure language remains agnostic (e.g., use "Solution" instead of "App").
- Clearly demarcate proven facts from assumptions using `[CONFIRMED]` and `[UNCONFIRMED]` markers.
- Never fake user personas or edge cases; derive them strictly from the user's Context Gathering dump.

## Final Output Destination
Write the approved, refined markdown content to: `exploration/sessions/session-brief.md` (or a timestamped equivalent).
