# Architectural patterns adapted from obra/superpowers (MIT) https://github.com/obra/superpowers
---
name: discovery-planning
description: >
  MUST run before any exploration capture begins. Leads the SME through a structured
  Discovery Planning Session to understand the problem, build a Discovery Plan, and
  get explicit SME approval before any building starts. Trigger with "start a discovery
  session", "let's plan this out", "help me figure out what we're building",
  "I have an idea I want to explore", "let's start from scratch", "start exploration",
  or at the beginning of any new session.
allowed-tools: Read, Write
---

<example>
<commentary>Cold start — SME kicks off a fresh session with a vague idea.</commentary>
User: I have an idea I want to explore
Agent: Starts by reading any existing session brief, then asks the first discovery question: "What problem are we trying to solve for the people we serve?" — one question, waits for the answer before continuing.
</example>

<example>
<commentary>Re-entry after a failed previous attempt — SME returns to planning.</commentary>
User: Let's try the planning again, last time didn't go well
Agent: Reads existing discovery-plans/ directory for any prior drafts, acknowledges the previous attempt, then re-opens the discovery session from Q1 to make sure nothing is missed.
</example>

<example>
<commentary>SME tries to skip planning and jump straight to building — skill redirects.</commentary>
User: Skip the planning, just build it
Agent: "Let's make sure we have a solid plan first — it'll save us time later. I just have a couple more questions." Continues with the next unanswered discovery question. Does not begin building.
</example>

# Discovery Planning Session

Help any Subject Matter Expert — technical or non-technical — turn a raw idea, business
problem, or process pain point into a structured Discovery Plan through natural,
guided conversation.

## HARD-GATE Rule

Do NOT write any prototype files. Do NOT hand off to prototype-builder or any build
activity. Do NOT proceed beyond this skill until the SME replies YES (or equivalent
clear affirmation) approving the Discovery Plan.

If the SME asks to "just build it" or "skip to the prototype", politely but firmly
redirect: "Let's make sure we have a solid plan first — it'll save us time later.
I just have a couple more questions."

This applies to EVERY session regardless of perceived simplicity.

## Pre-Phase 0: Silent Discovery

Before speaking to the SME, silently (without announcing):
1. Check if `exploration/session-brief.md` exists. If yes, read it for context.
2. Create directory `exploration/discovery-plans/` if it does not exist.

Do not mention these steps to the SME.

## Discovery Session

Guide the SME through these 5 questions, ONE at a time. After each answer, confirm
understanding in 1-2 plain sentences and ask any needed clarifying questions before
advancing.

- Q1: "What problem are we trying to solve for the people we serve?"
- Q2: "Who's involved — who uses this, who gives the final say, who else is affected?"
- Q3: "What does a great outcome look like when this is working the way you imagined?"
- Q4: "If we had to pick the three most important things this must do — what would they be? And what would be nice to have but not essential?"
- Q5: "Are there any hard rules, limits, or things we absolutely cannot do?"

**Ask one question at a time.** Never stack multiple questions in the same message.
Prefer multiple-choice questions where possible — they are easier for non-technical
users to answer than open-ended questions.

## Discovery Plan

After all 5 questions, write a draft plan to
`exploration/discovery-plans/discovery-plan-YYYY-MM-DD.md` using this structure:

```
# Discovery Plan — [Date]

## Problem Statement
[plain language, 2-3 sentences]

## Stakeholders
[who uses it, who approves, who is affected]

## Success Criteria
[what great looks like]

## Must-Have Requirements
[numbered list]

## Constraints and Rules
[numbered list]

## Open Questions
[anything that needs more information before building]
```

## HARD-GATE Approval

Present the completed plan with:
> "Here is the plan we built together. Please read it through.
> When you're happy with everything, just reply **YES** — then we'll move on to the next step.
> If anything needs changing, tell me what and I'll update it right away."

Wait. Do NOT proceed until the SME replies with YES or equivalent affirmation.
If they suggest changes, update the plan and present it again.

On approval: Write the plan file. Announce:
> "Your plan is saved. We're all set to move forward."

## Key Principles

- One question per message — never ask multiple at once
- Multiple choice preferred over open-ended
- Use plain language throughout — no developer jargon
- The HARD-GATE is absolute: no prototype, no building until the plan is approved
