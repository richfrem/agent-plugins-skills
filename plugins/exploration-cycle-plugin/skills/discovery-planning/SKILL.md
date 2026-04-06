---
name: discovery-planning
description: >
  MUST run before any exploration capture begins. Leads the SME through a structured
  Discovery Planning Session to understand the problem, propose 2-3 solution
  approaches, build a Discovery Plan, and get explicit SME approval before
  dispatching any documentation or prototype agents. Trigger with "start exploration",
  "let's plan this out", "I have an idea", "help me scope this", or at the beginning
  of any new Opportunity 3 session.
---

# Discovery Planning Session

Help any Subject Matter Expert — technical or non-technical — turn a raw idea, business
problem, or process pain point into a structured Discovery Plan through natural,
guided conversation.

Start by understanding the current context, then ask one question at a time to refine
the idea. Once you understand what we are going to explore, present the plan and get
the SME's explicit approval before anything is documented or built.

<HARD-GATE>
Do NOT dispatch any documentation agents (requirements-doc-agent, prototype-companion-agent,
business-rule-audit-agent, handoff-preparer-agent) or trigger any prototype-building
activity until you have presented a Discovery Plan and the SME has explicitly approved it.
This applies to EVERY session regardless of perceived simplicity.
</HARD-GATE>

## Anti-Pattern: "This Is Too Simple to Need a Plan"

Every session goes through this process. A simple automation, a process improvement,
a documentation need — all of them. Simple problems are where unexamined assumptions
cause the most wasted effort. The plan can be brief (a few sentences), but you MUST
present it and get approval.

## Discovery Planning Checklist

Complete these steps in order:

1. **Understand the context** — ask the SME what they are trying to solve, improve, or build
2. **Offer the Visual Companion** (if visual layouts or process flows are involved) — offer it once in its own message, get consent before proceeding
3. **Ask clarifying questions** — one at a time. Focus on: purpose, who is affected, what success looks like, any known constraints
4. **Propose 2-3 approaches** — lay out the options conversationally, with trade-offs and your recommendation
5. **Present the Discovery Plan** — summarise the agreed direction in plain language, section by section, get SME approval
6. **Write the Discovery Plan** — save to `exploration/discovery-plans/YYYY-MM-DD-<topic>-plan.md`
7. **Self-Review the Plan** — scan for vague sections, contradictions, unanswered questions (see Spec Alignment Checker below)
8. **SME Review Gate** — ask the SME to confirm the written plan before any agents are dispatched
9. **Transition to capture** — invoke the exploration-workflow skill to begin the capture phase

## How to Run the Session

**Ask one question at a time.** Never ask multiple questions in the same message.
Prefer multiple-choice questions where possible — they are much easier for non-technical
users to answer than open-ended questions.

**Understand the problem space:**
- What is the problem, opportunity, or idea?
- Who is affected by it?
- What would "success" look like in plain language?
- Are there known constraints, deadlines, or non-negotiables?

**If the scope seems very large:**
Flag it immediately. Help the SME decompose into smaller explorations. What are the
independent pieces? What should be explored first?

**Propose 2-3 approaches:**
Always present options before committing. Include your recommendation and why.
Present in plain business language — no technical jargon.

**Present the Discovery Plan in sections:**
- Problem Statement
- Who Is Affected
- What We Are Going to Explore
- Proposed Approach
- What Success Looks Like
- Known Constraints and Risks
- What We Will Build or Document

Ask after each section if it looks correct. Be ready to revise.

## Writing the Discovery Plan

After approval, write the plan to `exploration/discovery-plans/YYYY-MM-DD-<topic>-plan.md`.

Then run the self-review (Spec Alignment Checker below).

Then ask the SME to review the written plan:
> "I've written up our Discovery Plan. Please read it and let me know if anything looks
> wrong or is missing before I start gathering the details."

Wait for explicit approval. Only after approval: invoke `exploration-workflow` to begin
gathering the details.

## Spec Alignment Checker (Self-Review)

After writing the Discovery Plan, review it with fresh eyes:

1. **Vagueness scan:** Any sections that say "TBD", "to be determined", or "handle later"? Fix them.
2. **Contradiction check:** Does any section conflict with another? Pick one interpretation and make it explicit.
3. **Scope check:** Is this focused enough for one exploration session? If not, decompose.
4. **Ambiguity check:** Could any requirement be interpreted two different ways? Make the chosen interpretation explicit.

Fix inline. Do not re-review — just fix and move on.

## Visual Companion

Offer the Visual Companion when the session will involve layouts, process flows, or
interface design. Offer it once in its own message — do not combine with questions:

> "Some of what we're exploring might be easier to understand if I can show it to you
> visually in a browser — mockups, process diagrams, layout options. Would you like me
> to use that when helpful?" 

After consent, read and follow `skills/visual-companion/SKILL.md` for per-question
routing decisions (browser vs plain text).

## Key Principles

- One question per message — never ask multiple at once
- Multiple choice preferred over open-ended
- Always propose 2-3 approaches before committing
- Use plain business language throughout — no developer jargon
- The HARD-GATE is absolute: no capture, no prototype until the plan is approved
