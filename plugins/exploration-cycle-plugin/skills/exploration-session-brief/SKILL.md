---
name: exploration-session-brief
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

> ⚠️ **STUB** — `execute.py` not yet implemented. Use the [intake-agent](../../agents/intake-agent.md) for the real logic.

This skill provides a structured, 3-stage interactive workflow for generating an Exploration Session Brief. It replaces the boilerplate execution script with an active conversational agent pattern.

**Important Note for Agents:** Do NOT passively run a bash script or dump a massive block of markdown. You must guide the user through the following 3 stages.

## Stage 1: Context Gathering
Your goal is to understand the boundaries of the exploration *before* drafting anything. Ask the user:
1. **Domain Check:** What type of exploration is this? (e.g., Software feature, Business process improvement, Risk mitigation strategy, Research spike).
2. **Current State:** What is the specific problem or trigger that caused us to start this session?
3. **Information Dump:** Do you have any raw notes, transcripts, or links to provide as initial context? 
*(Tell the user they can brain-dump information safely).*

Wait for their response before proceeding.

## Stage 2: Section-by-Section Refinement
Instead of writing the entire brief at once, build it iteratively with the user.
1. **Propose the Outline:** Based on the domain identified in Stage 1, propose a numbered list of sections for the brief (e.g., Problem Statement, Stakeholders, Current Friction, Unknowns/Assumptions).
2. **Curate:** Ask the user if this outline looks right or if they want to add/remove sections.
3. **Draft & Edit:** For each section (or the whole document if it's short), present a draft. Ask the user: *"What should we keep, cut, or change?"* Apply surgical edits based on their feedback.

## Stage 3: Reader Testing (Blind Spot Analysis)
Once the draft is complete, ensure it holds up to scrutiny:
1. Predict 3 questions that someone entirely new to this project (e.g., an engineer or a new stakeholder) would ask when reading this brief.
2. Tell the user what those 3 questions are. 
3. If the brief doesn't answer them, ask the user if we should add answers or explicitly list them in the `## Open Questions` section of the brief.

## Anti-Hallucination Rules
- Do NOT assume the output will be a software product unless the user says so. Ensure language remains agnostic (e.g., use "Solution" instead of "App").
- Clearly demarcate proven facts from assumptions using `[CONFIRMED]` and `[UNCONFIRMED]` markers.
- Never fake user personas or edge cases; derive them strictly from the user's Context Gathering dump.

## Final Output Destination
Write the approved, refined markdown content to: `exploration/sessions/session-brief.md` (or a timestamped equivalent).
