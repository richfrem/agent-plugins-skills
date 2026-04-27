---
name: discovery-planning
plugin: exploration-cycle-plugin
description: >
  Guides a Subject Matter Expert through a structured discovery session to create and approve a Discovery Plan before any building begins. This is the HARD-GATE brainstorming skill — no prototype can be built until the SME explicitly approves the plan. Trigger phrases: "start a discovery session", "let's plan this out", "help me figure out what we're building", "I have an idea I want to explore", "let's start from scratch"
allowed-tools: Read, Write
---
# Architectural patterns adapted from obra/superpowers (MIT) https://github.com/obra/superpowers


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

## Session Type Fork

**Read the session type before asking any questions.** Check in this order:
1. The `## Session Context` block passed by the orchestrator (look for `Session type:`)
2. `**Session Type:**` field in `exploration/exploration-dashboard.md`
3. If neither is available, ask: *"What kind of session is this — are we building something new, improving an existing system, documenting a process, or investigating a question?"*

Route to the correct track:

| Session Type | Question Track |
|---|---|
| Greenfield / website / new app | **Standard Track** (Q1–Q6 below) |
| Brownfield — feature addition | **Feature Addition Track** (FQ1–FQ5 below) |
| Brownfield — legacy analysis / replatforming | **Legacy/Brownfield Track** (LQ1–LQ6 below) |
| Analysis/Docs — process | **Process Intervention Track** (PQ1–PQ5 below) |
| Analysis/Docs — strategic | **Strategic Planning Track** (SQ1–SQ5 below) |
| Analysis/Docs — risk/compliance | **Risk Assessment Track** (RQ1–RQ5 below) |
| Analysis/Docs — requirements | **Standard Track** — requirements gathering uses the same questions, just without prototype output |
| Spike | **Open Exploration Track** (OQ1–OQ4 below) |

Do not mention this routing to the SME. Just use the correct track.

---

## Assumptions Check (All Session Types)

Before asking the first discovery question, ask these two questions together in one message. Frame them as time-savers, not interrogation:

> "Before we dive in — a couple of quick questions that have saved teams weeks before:
>
> 1. Have you already checked whether something like this exists in your current systems or tools?
> 2. Is this about access to information that's hard to find, or information that genuinely doesn't exist yet?"

Listen carefully to the answers:
- If the SME indicates **it already exists but is hard to access** → gently surface this: *"It sounds like this might be a visibility or access problem rather than a build problem. Let's explore that — it could be a much faster fix."* Continue with discovery questions framed around access/process rather than new software.
- If the SME indicates **it definitely doesn't exist** → proceed with the relevant discovery track.
- If the SME is **unsure** → note this as an open question. Continue with discovery and revisit at the Intervention Check.

Do not block progress on the Assumptions Check — it is a signal, not a gate.

---

## Discovery Session

Guide the SME through the following questions, **one at a time**. After each answer:
- Confirm your understanding in 1–2 plain sentences ("Here's what I heard — does this look right?")
- Ask any needed clarifying questions before moving to the next
- Never ask more than one question at a time

---

## Legacy/Brownfield Track

Use this track when `**Session Type:**` contains `brownfield` or `legacy analysis`. These questions are tuned for understanding an existing system rather than imagining a new one.

**LQ1:** "What does the current system do that people genuinely depend on — the things that would break something if they disappeared?"

**LQ2:** "What's broken, missing, or causing pain right now? What makes people frustrated with it today?"

**LQ3:** "Who are the people who truly understand how this works — and are they still here? Is there undocumented knowledge we need to capture before it's lost?"

**LQ4:** "What other systems, tools, or processes does this connect to? What would break if we changed or removed it?"

**LQ5:** "What's the goal — are we replacing it, supplementing it, documenting it for safety, or planning a migration to something modern?"

**LQ6:** "Are there hard constraints on the path forward — things we can't change, integrations that must survive, compliance requirements, or a timeline driven by something external?"

After all six brownfield questions are answered, go directly to the Discovery Plan section below. Skip the Standard Track and the Intervention Check (it's implicit in LQ5 — the SME has already answered what kind of outcome they need).

---

## Feature Addition Track

Use when `**Session Type:**` is `Brownfield — feature addition`. Focus on what exists, what's changing, and why now.

**FQ1:** "Tell me about the system we're adding to — what does it do today and who uses it?"

**FQ2:** "What's the feature or change you want to add? What's the trigger — what problem or opportunity is driving this now?"

**FQ3:** "Who will use this new feature and what does success look like for them?"

**FQ4:** "Are there things the current system does that this change must not break? What are the non-negotiables?"

**FQ5:** "Are there any technical constraints or integration requirements I should know about going in?"

After all five answers, go to the Discovery Plan section below.

---

## Process Intervention Track

Use when `**Session Type:**` is `Analysis/Docs — process`. Start with the Intervention Check — this scenario is the most likely to reveal that software isn't the answer.

**PQ1 (Intervention Check first):** "Walk me through how the process works today — step by step, from the moment it starts to when it's done. Where does it break down or create the most friction?"

Listen carefully. Before asking the next question, assess: is this a software problem, or a process/policy/people problem? Surface the distinction:
> "Based on what you're describing, I want to check something before we go further. [Reflect the problem back.] Does it feel like the core issue is that people don't have the right tool — or that the steps, rules, or handoffs are wrong?"

If non-software: acknowledge it as the better answer. Continue with the remaining questions framed around process change, not software.

**PQ2:** "Who is affected by this process — both the people doing the work and the people waiting for the outcome?"

**PQ3:** "What does 'fixed' look like? What would need to be true for this to be considered resolved?"

**PQ4:** "Are there any constraints on what can change — regulatory requirements, systems that can't be touched, teams that can't be reorganised?"

**PQ5:** "Has anyone tried to fix this before? What happened and why didn't it stick?"

After all five answers, go to the Discovery Plan section below.

---

## Strategic Planning Track

Use when `**Session Type:**` is `Analysis/Docs — strategic`. Focus on decisions, options, and constraints — not features.

**SQ1:** "What decision needs to be made, and when does it need to be made by? What happens if it isn't made?"

**SQ2:** "Who are the key stakeholders — who has a say, who is affected, and whose buy-in is essential?"

**SQ3:** "What constraints are non-negotiable — budget, timeline, regulatory requirements, things that are already decided?"

**SQ4:** "What does a good outcome look like in 12–24 months? How will you know the right decision was made?"

**SQ5:** "What's the risk of doing nothing, or delaying? What's driving the urgency?"

After all five answers, go to the Discovery Plan section below. The handoff for this track is a Strategic Recommendation document, not a prototype spec.

---

## Risk Assessment Track

Use when `**Session Type:**` is `Analysis/Docs — risk/compliance`.

**RQ1:** "What's the risk or compliance gap we're assessing — what triggered this and what's at stake if it isn't addressed?"

**RQ2:** "What regulations, standards, or internal policies apply? Are there any external auditors or certifications involved?"

**RQ3:** "What does the current state look like — what controls exist today and where are the gaps?"

**RQ4:** "What does 'resolved' look like — what would a regulator, auditor, or risk committee need to see to sign off?"

**RQ5:** "Are there constraints on the remediation path — technology choices already made, timelines, budget limits, or teams that own specific areas?"

After all five answers, go to the Discovery Plan section below. The handoff for this track is a Risk Assessment or Policy document.

---

## Open Exploration Track

Use when `**Session Type:**` is `Spike`. Keep structure light — the goal is to generate and test hypotheses, not converge prematurely.

**OQ1:** "What's the question or hypothesis we're investigating? What would we need to learn or prove to feel confident moving forward?"

**OQ2:** "What do we already know — what context, data, or prior attempts exist that we should start from?"

**OQ3:** "What would a useful answer look like at the end of this session — a decision, a direction, a prototype, or just clearer questions?"

**OQ4:** "Are there any boundaries on the investigation — things we've already ruled out, or areas we can't explore?"

After all four answers, go to the Discovery Plan section below. Note: for spikes, the Discovery Plan is a lightweight investigation brief, not a full requirements document.

---

## Standard Track

### Part 1: Understanding the Problem

**Q1:** "What problem are we trying to solve for the people we serve?"

**Q2:** "Who's involved — who uses this, who gives the final say, who else is affected?"

**Q3:** "What does a great outcome look like when this is working the way you imagined?"

### Part 2: Right Problem, Right Intervention

After Q3, pause and reflect. Based on what you've heard, consider whether the problem
the SME described is actually a technology problem, or whether it might be:
- A **process problem** — the steps are in the wrong order, or a handoff is broken
- A **policy or rules problem** — the rules are confusing, contradictory, or create failure demand
- A **communication problem** — people don't understand what's available or what to do
- A **data or access problem** — the information exists but isn't reaching the right people

**Q4 (Intervention Check):** Reflect what you heard, then ask:

> "Before we go further — based on what you've described, I want to make sure we're
> solving the right problem. Sometimes the best fix isn't a new tool or system — it's
> changing a rule, simplifying a process, or removing a step entirely.
>
> When people hit this problem today, what actually goes wrong for them? Is it that they
> don't have the right tool, or is it something about how the process or rules work?"

This question is critical. Listen carefully to the answer. If the SME describes a process
or policy issue rather than a technology gap, gently surface it:

> "It sounds like the core issue might be [process/policy/communication problem], not
> necessarily a technology gap. If we [simplified the rule / changed the sequence /
> clarified the guidance], would that solve most of it without building anything new?"

**If the SME agrees the problem is non-technical:**
1. Acknowledge: *"That's actually a great outcome — you've just saved the cost of building something that wouldn't have solved it."*
2. Update the session type: if the dashboard exists and `**Session Type:**` is currently Greenfield or Brownfield, change it to `Analysis/Docs — [process / policy / communication]` with a note explaining the pivot. If the dashboard doesn't exist yet (standalone use), note this in the Discovery Plan.
3. The deliverable becomes the process change recommendation, policy update, or communication fix — not a software prototype. Phase 3 is now disabled.
4. Continue to Q5–Q6 with this framing: "requirements" means the criteria for a successful process or policy change, not software features.

**If the SME confirms they need a technical solution:** Proceed. The intervention check
still adds value — it sharpens the problem statement and prevents solutioneering.

**If it's mixed (both a process gap AND a technology gap):**
Note both dimensions explicitly in the Intervention Type section of the Discovery Plan.
Flag which is primary. The handoff should address both: the non-technical fixes the team can act on immediately, and the technical requirements that justify a build.

### Part 3: Requirements and Constraints

Adapt Q5 and Q6 based on what the Intervention Check revealed:

**If the outcome is software (new app, feature, automation, website, integration):**

**Q5:** "If we had to pick the three most important things this must deliver — what would they be? And what would be nice to have but not essential?"

**Q6:** "Are there any hard rules, limits, or things we absolutely cannot do? (e.g., must work on mobile, must integrate with [system], must not store personal data)"

**If the outcome is a process or workflow change:**

**Q5:** "What would need to be true for this process to be considered fixed? What are the three things that matter most to the people who use it every day?"

**Q6:** "Are there any constraints on what we can change? (e.g., regulatory requirements, systems we can't touch, teams we can't reorganise)"

**If the outcome is a strategic plan or decision document:**

**Q5:** "What does a good decision here actually look like? What would you need to know or see to feel confident moving forward?"

**Q6:** "Are there any boundaries on the options we should consider — budget, timeline, organisational constraints, things that are already decided?"

**If the outcome is legacy system analysis or modernisation planning:**

**Q5:** "What are the most important things the current system does that any replacement must also do? And what does it do that nobody would miss if it disappeared?"

**Q6:** "Are there constraints on the modernisation path — technology choices already made, integrations that must survive, compliance requirements, or a timeline?"

**If the outcome is policy, compliance, or risk documentation:**

**Q5:** "What does 'good enough' look like here — what would make the risk or compliance gap considered resolved?"

**Q6:** "Are there external standards, regulations, or existing policies that any recommendation must align with?"

After each answer, reflect back what you heard before moving forward:
> "So if I'm understanding correctly, [summary]. Does that sound right?"

Only advance to the next question once the SME confirms your summary is correct.

## Discovery Plan

After all 6 questions are answered and confirmed, write a draft plan to:

`exploration/discovery-plans/discovery-plan-YYYY-MM-DD.md`

Use this exact structure — adapt the section labels in brackets to fit the scenario (guidance in parentheses):

```
# Discovery Plan — [Date]
**Session type:** [Greenfield / Brownfield — feature / Brownfield — legacy analysis /
                   Analysis — process / Analysis — strategic / Analysis — risk/compliance /
                   Spike]

## Problem Statement
[plain language, 2-3 sentences — what's wrong or missing, for whom, and why it matters now]

## Intervention Type
[Resolved from the Intervention Check — be explicit]
- Primary: [Software — new app / feature / automation / website / integration]
         OR [Process change — describe the change needed]
         OR [Policy or rules change — describe the rule causing friction]
         OR [Communication fix — describe what guidance is missing]
         OR [Strategic decision — describe the decision to be made]
         OR [Legacy analysis — describe what system is being understood]
- Supporting (if mixed): [secondary intervention, if any]
- Software needed: yes / no / not yet determined

## Stakeholders
- Users: [who interacts with the solution day-to-day]
- Decision maker: [who approves / signs off]
- Affected parties: [who else is impacted]

## Success Criteria
[what great looks like when this is solved — use the SME's own words where possible]

## Must-Have Requirements
[numbered list — use language appropriate to the outcome type:
  software → functional requirements
  process → steps or criteria that must change
  strategic → questions that must be answered
  legacy analysis → systems or capabilities that must be documented]

## Constraints and Rules
[numbered list — hard limits, non-negotiables, regulatory requirements]

## Open Questions
[anything unresolved that Phase 2+ or the handoff will need to address]
```

Use plain language throughout. No technical jargon. Write for the SME, not for engineers.

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

Output this machine-readable block so the orchestrator can parse phase completion:

~~~
## HANDOFF_BLOCK
PHASE: 1
STATUS: COMPLETE
OUTPUT: exploration/discovery-plans/discovery-plan-YYYY-MM-DD.md
SESSION_TYPE: [value from dashboard or classification]
INTERVENTION_TYPE: [software / process / strategic / legacy-analysis / risk-compliance / spike]
OPEN_QUESTIONS: [count of items in ## Open Questions section]
~~~

## Gotchas

- **Dashboard intercept ordering**: The dashboard intercept runs before the HARD-GATE check. If the dashboard status field is missing (file corrupted), the intercept will not fire and this skill will run standalone instead of redirecting. Always write `**Status:**` as the first field in a new dashboard.
- **Assumptions Check is not a gate**: The two assumptions questions must not block progress — but agents sometimes treat "I'm not sure" as a blocker. If the SME is unsure, note it as an open question and continue.
- **Legacy/Brownfield track skips Intervention Check**: The Intervention Check is implicit in LQ5. Do NOT re-run Q4 from the Standard Track for brownfield sessions — it will confuse the SME with redundant questions.
- **Discovery Plan date in filename vs content**: The plan file uses `YYYY-MM-DD` in both the filename and the `# Discovery Plan — [Date]` header. If the session spans midnight, these may differ. Use the date when the plan was approved, not when the session started.
- **Spike re-entry loses plan context**: When archiving a prior spike discovery plan (iteration N), ensure the new Phase 1 starts with a brief showing the prior plan path. The SME should not have to re-describe their idea from scratch.

## Completion — Return to Orchestrator

If operating within an active Exploration Session (i.e., `exploration/exploration-dashboard.md`
exists and `**Status:**` is not `Complete`):
1. Say to the user:
   > "Returning to your session dashboard now."
2. **Return to the orchestrator.** Use the Skill tool: `skill: "exploration-workflow"`.
   After invoking it, stop generating output from this skill.
   If the Skill tool is not available in your harness, tell the user:
   *"Please run `/exploration-workflow` to continue your session."*

If operating standalone (no dashboard file, or `**Status:** Complete`), the skill is complete.
