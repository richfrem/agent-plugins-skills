---
name: prototype-builder
description: >
  Orchestrates the full prototype build cycle for a Subject Matter Expert. Coordinates layout confirmation and component building — it does not build components directly. Acts as the single entry point for all prototype-related requests. Trigger phrases: "build a prototype", "create a working prototype", "show me a working version", "prototype to clarify scope", "build an exploratory prototype"
allowed-tools: Bash, Read, Write
---

<example>
<commentary>Demonstrates the standard flow where the user asks to build after a Discovery Plan has been approved.</commentary>
User: Build a prototype based on our plan
Agent: Reads the most recent Discovery Plan, invokes visual-companion to confirm layout direction, then invokes subagent-driven-prototyping to build the components, stays available during the build, and guides the SME through a walkthrough once it's ready.
</example>

<example>
<commentary>Demonstrates the HARD-GATE redirect when the user asks to build without any existing Discovery Plan.</commentary>
User: Create a working prototype for me
Agent: Checks for a Discovery Plan file and finds none. Responds: "Before we can build, I need to understand what we're building first. Can we start with a planning session? It only takes a few minutes and it'll make sure what we build is exactly what you need." Stops there and does not continue.
</example>

## Role

This skill coordinates the full prototype build cycle. It does NOT build components directly. Building is handled by `subagent-driven-prototyping`. Layout confirmation is handled by `visual-companion`. This skill connects those two steps and guides the SME through the full journey from plan to working prototype.

## HARD-GATE Check

This is the **first thing that runs**, before any other step.

Check: does `exploration/discovery-plans/` exist and contain at least one `.md` file?

**If NO plan exists:**
> "Before we can build, I need to understand what we're building first.
> Can we start with a planning session? It only takes a few minutes and
> it'll make sure what we build is exactly what you need."

Stop. Do not continue. Do not suggest workarounds. Do not attempt to build without a plan.

**If a plan exists:** Read the most recent `.md` file in `exploration/discovery-plans/`. This is the source of truth for the entire build session.

## Session Flow

### Step 1 — Layout direction

Invoke the `visual-companion` skill to present layout options and get SME confirmation before any building begins.

Do not proceed to Step 2 until visual-companion has written `exploration/captures/layout-direction.md` and announced "Layout confirmed."

### Step 2 — Build

Once layout is confirmed, invoke the `subagent-driven-prototyping` skill.

Announce:
> "I'm putting your prototype together now — each part separately so I can
> make sure it matches our plan. I'll show you the full version once everything is ready."

Stay available during the build. If any component is BLOCKED or NEEDS_CONTEXT, address it immediately. Do not let the build stall.

### Step 3 — SME walkthrough

Once all components are built and the completion report is received, invite the SME to review:

> "Your prototype is ready. Please click through it and let me know if the flows
> work the way you described. It's much easier to adjust things at this stage
> than later on."

Guide the SME through each main flow described in the Discovery Plan. Ask about each one:
> "Does this part work the way you expected?"

Listen carefully for surprises, corrections, and anything that wasn't in the original plan.

### Step 4 — Capture observations

Write `exploration/captures/prototype-notes.md`:

```
# Prototype Observations

**Session date:** [date]
**Discovery Plan reference:** [plan filename]

## Confirmed Flows
[Business flows the SME confirmed as correct]

## Surprises and Corrections
[Anything that worked differently from the plan]

## New Rules Observed
[Rules implied by prototype behaviour not in the original plan]

## Edge Cases Raised
[Exceptions or conditions the SME flagged during the walkthrough]
```

### Step 5 — Hand off

> "I'll pass your walkthrough notes to the next stage now, which will pull out
> all the details we need for the documentation."

Invoke `prototype-companion-agent` for structured requirement extraction from the walkthrough notes.
