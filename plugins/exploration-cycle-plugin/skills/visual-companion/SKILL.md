---
name: visual-companion
description: >
  Presents layout options to the SME in plain language before any prototype construction begins. Invoked after the Discovery Plan is approved to confirm visual structure and direction. Trigger phrases: "what should it look like", "show me some layout options", "let me see the design options before we build". Also invoked by prototype-builder after plan approval.
allowed-tools: Read, Write
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
<commentary>Demonstrates a direct user trigger asking to see layout options before building starts.</commentary>
User: What should it look like?
Agent: Reads the most recent Discovery Plan for context, then presents three plain-language layout options labelled Option A, Option B, and Option C — adapted to the specific problem domain — and asks the SME which feels closest to what they had in mind.
</example>

<example>
<commentary>Demonstrates the skill being invoked by prototype-builder as part of the coordinated build cycle.</commentary>
User: [dispatched by prototype-builder after Discovery Plan approval]
Agent: Reads the Discovery Plan silently, presents three contextually adapted layout options in plain language, confirms the SME's selection, and writes the confirmed layout direction to exploration/captures/layout-direction.md before signalling ready to build.
</example>

## Skippable Phase

This phase may be skipped for brownfield sessions or simple features where the design is straightforward. If skipped, it will be marked `- [~]` in the dashboard. The downstream Phase 3 skill handles missing layout direction gracefully.

## Role

This skill is invoked after the Discovery Plan is approved. Its purpose is to confirm the **structure and shape** of the output before any building or drafting starts. For software, this means UI layout. For non-software work, this means document structure, process flow shape, or analysis format. It ensures the SME has a clear picture of what they are agreeing to before anything is created.

## Session Flow

### Step 1 — Read context and determine output type

Read the most recent file in `exploration/discovery-plans/`. Understand the problem domain, stakeholders, and success criteria before proposing anything. Do not skip this step.

Determine the **output type** from the Discovery Plan and session type:
- **Software UI** — the output is a screen, page, or interactive interface
- **Process or workflow** — the output is a business process, approval chain, or operational flow
- **Document or analysis** — the output is a report, requirements doc, policy, or strategic plan
- **Mixed** — some combination of the above

### Step 2 — Present 3 options (adapted to output type)

Offer 3 structure options adapted to the context of the Discovery Plan. Describe each in plain language (2–4 sentences). No technical terms. No code. No wireframes. Words only.

Label them **Option A**, **Option B**, **Option C**.

**For software UI outputs**, adapt these starting points:

- **Option A:** A single-page view with a summary at the top and details below — good when people need to see everything at once and make decisions without switching screens
- **Option B:** A step-by-step flow that walks the user through one thing at a time — good when there's a sequence of decisions, approvals, or actions that need to happen in order
- **Option C:** A two-panel layout with a list on the left and details on the right — good when people need to browse through a number of items and compare them before deciding

**For process or workflow outputs**, adapt these starting points:

- **Option A:** A linear flow — steps happen in a fixed order from start to finish, good for simple processes with no branches
- **Option B:** A decision-tree flow — the path branches based on conditions or approvals, good when different situations lead to different actions
- **Option C:** A swimlane view — shows who does what at each stage, good when multiple people or teams are involved and handoffs matter

**For document or analysis outputs**, adapt these starting points:

- **Option A:** Executive summary up front with supporting detail sections — good when the audience wants the answer first and the reasoning second
- **Option B:** Problem → Analysis → Recommendations structure — good when the audience needs to follow the logic to be convinced
- **Option C:** Comparison format with side-by-side options — good when the deliverable is about choosing between alternatives

After presenting the three options, ask:
> "Which of these feels closest to what you had in mind? Or if none of them fit, describe what you're picturing and I'll work with that."

### Step 3 — Confirm selection

Reflect back the chosen option in one sentence. For example:
> "Got it — we'll go with a step-by-step flow so your team can move through each approval in order."

Then ask: "Is there anything you'd like to adjust about that?"

Wait for the SME's response before proceeding.

### Step 4 — Save direction

Write `exploration/captures/layout-direction.md` with this structure:

```
# Layout Direction

**Selected:** [Option letter and name]
**SME notes:** [any modifications or specific requests the SME mentioned]
**Confirmed:** [date]
```

### Step 5 — Signal ready

Announce: "Layout confirmed — Phase 2 is complete."

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
