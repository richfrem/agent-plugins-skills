# Architectural patterns adapted from obra/superpowers (MIT) https://github.com/obra/superpowers
---
name: discovery-planning
description: >
  Guides a Subject Matter Expert through a structured discovery session to create and approve a Discovery Plan before any building begins. This is the HARD-GATE brainstorming skill — no prototype can be built until the SME explicitly approves the plan. Trigger phrases: "start a discovery session", "let's plan this out", "help me figure out what we're building", "I have an idea I want to explore", "let's start from scratch"
allowed-tools: Read, Write
---

## Dashboard Intercept

Before doing anything else, silently check for `exploration/exploration-dashboard.md`.

- **If the file EXISTS:** Stop immediately. Do not proceed with this skill's standalone flow.
  Announce to the user:
  > "It looks like you have an active Exploration Session in progress. Let me take you back
  > to your session dashboard so we can keep your progress on track."
  Then invoke `exploration-workflow` to resume from the correct phase.

- **If the file does NOT exist:** Proceed with this skill's standalone flow as normal.

<example>
<commentary>Demonstrates a cold start where the user opens a brand new session with no prior context.</commentary>
User: I have an idea I want to explore
Agent: Welcomes the SME warmly, silently checks for any existing session brief, then asks the first discovery question: "What problem are we trying to solve for the people we serve?"
</example>

<example>
<commentary>Demonstrates re-entry after a previously incomplete attempt — the skill picks up existing context and resumes.</commentary>
User: Let's plan this out, I tried before but it didn't go anywhere
Agent: Silently reads the existing session brief if present, acknowledges the SME's prior attempt in plain language, and picks up the discovery questions from where they left off — or starts fresh if no useful context exists.
</example>

<example>
<commentary>Demonstrates the HARD-GATE redirect when the user tries to skip planning and go straight to building.</commentary>
User: Can we just skip the planning and build it?
Agent: Politely but firmly redirects: "Let's make sure we have a solid plan first — it'll save us time later. I just have a couple more questions." Returns to the next unanswered discovery question.
</example>

## HARD-GATE Rule

Do NOT write any prototype files. Do NOT hand off to prototype-builder or any other skill. Do NOT proceed beyond this skill until the SME replies **YES** (or an equivalent clear affirmation) approving the Discovery Plan.

If the SME asks to "just build it" or "skip to the prototype", respond:
> "Let's make sure we have a solid plan first — it'll save us time later. I just have a couple more questions."

Then return to the next unanswered discovery question. Never skip the gate.

## Pre-Phase 0: Silent Discovery

Before speaking to the SME, silently (without announcing to the user):

1. Check if `exploration/session-brief.md` exists. If it does, read it for any useful context about the problem domain or stakeholders.
2. Create the directory `exploration/discovery-plans/` if it does not already exist.

Do not mention these steps to the SME.

## Discovery Session

Guide the SME through the following 5 questions, **one at a time**. After each answer:
- Confirm your understanding in 1–2 plain sentences ("Here's what I heard — does this look right?")
- Ask any needed clarifying questions before moving to the next
- Never ask more than one question at a time

**Q1:** "What problem are we trying to solve for the people we serve?"

**Q2:** "Who's involved — who uses this, who gives the final say, who else is affected?"

**Q3:** "What does a great outcome look like when this is working the way you imagined?"

**Q4:** "If we had to pick the three most important things this must do — what would they be? And what would be nice to have but not essential?"

**Q5:** "Are there any hard rules, limits, or things we absolutely cannot do?"

After each answer, reflect back what you heard before moving forward. Example:
> "So if I'm understanding correctly, [summary]. Does that sound right?"

Only advance to the next question once the SME confirms your summary is correct.

## Discovery Plan

After all 5 questions are answered and confirmed, write a draft plan to:

`exploration/discovery-plans/discovery-plan-YYYY-MM-DD.md`

Use this exact structure:

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

Use plain language throughout. No technical terms, no jargon.

## HARD-GATE Approval

Present the completed plan to the SME with:

> "Here is the plan we built together. Please read it through.
> When you're happy with everything, just reply **YES** — then we'll move on to the next step.
> If anything needs changing, tell me what and I'll update it right away."

Wait. Do NOT proceed until the SME replies with YES or an equivalent clear affirmation (e.g., "looks good", "that's right", "approved").

If they suggest changes:
1. Update the plan with the requested changes
2. Present the updated version
3. Ask again for approval

Repeat until the SME is satisfied.

On approval:
1. Write the final plan file to `exploration/discovery-plans/discovery-plan-YYYY-MM-DD.md`
2. Announce: "Your plan is saved — Phase 1 is complete."

## Completion — Return to Orchestrator

If operating within an active Exploration Session (i.e., `exploration/exploration-dashboard.md` exists):
> "Returning to your session dashboard now."
Then invoke `exploration-workflow` to trigger the Phase 1 HARD-GATE and dashboard update.

If operating standalone (no dashboard file), the skill is complete.
