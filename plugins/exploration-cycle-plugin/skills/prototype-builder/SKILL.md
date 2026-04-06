---
name: prototype-builder
description: >
  Builds a fully working, interactive prototype that the SME can click through
  to validate business flows. Use ONLY after the Discovery Plan is approved.
  Trigger with "build the prototype", "let's build it", "I want to see it working",
  "create a working version", or when the SME wants to validate their Discovery Plan
  with a real interactive experience rather than just documents.
allowed-tools: Bash, Read, Write
---

# Prototype Builder

Build a fully working, interactive prototype that the SME can click through,
fill in, and use to validate that the proposed solution matches what they need.

This is not a mockup, not a wireframe, and not a sketch. The SME must be able
to walk through real business flows and confirm — or correct — the logic.

<HARD-GATE>
Do NOT begin building until you have confirmed that an approved Discovery Plan
exists in `exploration/discovery-plans/`. If no approved plan exists, stop and
invoke the `discovery-planning` skill first. Building without an approved plan
wastes everyone's time.
</HARD-GATE>

## Step 1: Confirm the Discovery Plan is Approved

Check that an approved Discovery Plan exists:

```bash
ls exploration/discovery-plans/
```

If no approved plan exists: stop and invoke `discovery-planning` first.

If a plan exists, read it fully before proceeding. You will build exactly what
it describes — nothing more, nothing less.

## Step 2: Offer the Visual Companion for Layout Direction

Before building, confirm the visual layout direction with the SME. Invoke the
`visual-companion` skill for this step.

The layout-confirm question: show the SME 2-3 layout options for the prototype
and get their confirmation before building the full thing.

Ask: "Before I start building, would you like to see a few layout options so we
can pick the right look before I put everything together?"

If yes: use the Visual Companion to show 2-3 layout options. Build in the direction
the SME approves.

If no: proceed with a standard layout that matches the Discovery Plan context.

## Step 3: Build Component by Component

Invoke `subagent-driven-prototyping` to build the prototype.

Announce:
> "I'm building your prototype now. I'll build each part separately and check
> that it matches our plan before moving on. This keeps each piece clean and
> avoids mistakes carrying over between sections."

The `subagent-driven-prototyping` skill handles:
- Creating the prototype sandbox
- Dispatching a focused assistant per component
- Running the two-stage review (Plan Alignment → Quality Check)
- Reporting component status

Your role during this step: stay available to answer questions the focused
assistants raise. Do not intervene in the build unless a component is BLOCKED
or NEEDS_CONTEXT.

## Step 4: SME Validates the Working Prototype

Once all components are built and reviewed, invite the SME to walk through
the prototype:

> "Your prototype is ready. Please click through it and walk through the business
> flows we discussed. Let me know if anything works differently from what you
> expected — that's exactly the kind of feedback we want at this stage."

Guide the SME through each main flow described in the Discovery Plan. Note any
observations, surprises, or corrections they raise.

## Step 5: Capture Observations

After the SME walkthrough, write observations to:
`exploration/captures/prototype-notes.md`

Include:
- Business flows the SME confirmed as correct
- Anything that surprised the SME or worked differently from the plan
- New business rules implied by the prototype behaviour
- Edge cases or exceptions the SME raised during the walkthrough

Then dispatch the `prototype-companion-agent` to extract structured observations
from the session for use in the documentation phase.

## What a Good Prototype Looks Like

A prototype built by this skill must:
- Run locally without external dependencies (self-contained)
- Present real business flows — not placeholder "Lorem ipsum" content
- Accept input and show meaningful responses (not static pages)
- Be clickable end-to-end through at least one complete business scenario

A prototype that crashes, shows blank pages, or cannot be interacted with is
not done. Fix before presenting to the SME.

## Key Principles

- HARD-GATE is absolute: no building without an approved Discovery Plan
- Layout direction is confirmed BEFORE building (not after)
- Build component by component — never all at once
- The SME's walkthrough is part of the build, not optional
- Observations from the walkthrough feed directly into the documentation phase
