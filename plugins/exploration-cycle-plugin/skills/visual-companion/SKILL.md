---
name: visual-companion
description: >
  Presents layout options to the SME in plain language before any prototype construction begins. Invoked after the Discovery Plan is approved to confirm visual structure and direction. Trigger phrases: "what should it look like", "show me some layout options", "let me see the design options before we build". Also invoked by prototype-builder after plan approval.
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
<commentary>Demonstrates a direct user trigger asking to see layout options before building starts.</commentary>
User: What should it look like?
Agent: Reads the most recent Discovery Plan for context, then presents three plain-language layout options labelled Option A, Option B, and Option C — adapted to the specific problem domain — and asks the SME which feels closest to what they had in mind.
</example>

<example>
<commentary>Demonstrates the skill being invoked by prototype-builder as part of the coordinated build cycle.</commentary>
User: [dispatched by prototype-builder after Discovery Plan approval]
Agent: Reads the Discovery Plan silently, presents three contextually adapted layout options in plain language, confirms the SME's selection, and writes the confirmed layout direction to exploration/captures/layout-direction.md before signalling ready to build.
</example>

## Role

This skill is invoked after the Discovery Plan is approved. Its purpose is to confirm the visual structure of the prototype before any building starts. It ensures the SME has a clear picture of what they are agreeing to before anything is created.

## Session Flow

### Step 1 — Read context

Read the most recent file in `exploration/discovery-plans/`. Understand the problem domain, stakeholders, and success criteria before proposing anything. Do not skip this step.

### Step 2 — Present 3 options

Offer 3 layout options adapted to the context of the Discovery Plan. Describe each in plain language (2–4 sentences). No technical terms. No code. No wireframes. Words only.

Label them **Option A**, **Option B**, **Option C**.

Adapt these generic starting points to the specific problem and user group from the Discovery Plan:

- **Option A:** A single-page view with a summary at the top and details below — good when people need to see everything at once and make decisions without switching screens
- **Option B:** A step-by-step flow that walks the user through one thing at a time — good when there's a sequence of decisions, approvals, or actions that need to happen in order
- **Option C:** A two-panel layout with a list on the left and details on the right — good when people need to browse through a number of items and compare them before deciding

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

If operating within an active Exploration Session (i.e., `exploration/exploration-dashboard.md` exists):
> "Returning to your session dashboard now."
Then invoke `exploration-workflow` to trigger the Phase 2 HARD-GATE and dashboard update.

If operating standalone (no dashboard file), the skill is complete.
