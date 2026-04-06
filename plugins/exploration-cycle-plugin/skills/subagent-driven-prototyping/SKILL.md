---
name: subagent-driven-prototyping
description: >
  Use when building a prototype component-by-component against an approved Discovery Plan.
  Each component is built by a focused assistant with only the approved plan as context,
  then reviewed in two stages: Spec Alignment (does it match the plan?) then Prototype
  Quality (does it work?). Trigger with "build the prototype", "start building",
  "let's create the working prototype", or when the prototype-builder skill is active.
---

# Subagent-Driven Prototyping

Build a working prototype component by component, with a fresh focused assistant per
component and a two-stage review after each one.

**Why focused assistants:** Each prototype component is built by an assistant that only
knows the approved Discovery Plan and the current component's requirements. No context
pollution, no confusion from earlier components. This produces cleaner, more reliable work.

**Core principle:** Fresh assistant per component + two-stage review (plan alignment then
quality check) = a prototype the SME can actually click through and validate.

## When to Use

This skill is invoked by the `prototype-builder` skill after:
1. The Discovery Plan has been approved by the SME
2. The Visual Companion has confirmed the visual layout direction

Do NOT use this skill directly. It is always invoked by `prototype-builder`.

## The Process

### Setting Up the Prototype Sandbox

Before building, create an isolated working area:

```bash
# Create the prototype sandbox
mkdir -p exploration/prototypes/YYYY-MM-DD-<topic>
cd exploration/prototypes/YYYY-MM-DD-<topic>
```

Announce to the SME:
> "I'm setting up your prototype sandbox and building each component separately to
> make sure everything matches what we planned."

### Per-Component Loop

For each component in the Discovery Plan:

1. **Dispatch a focused assistant** — provide ONLY:
   - The approved Discovery Plan
   - The specific component requirements
   - The prototype sandbox location

2. **Focused assistant builds the component** — it should:
   - Build exactly what the Discovery Plan specifies (no extras)
   - Validate that the component works
   - Report back with status

3. **Stage 1 — Spec Alignment Review:**
   Read the approved Discovery Plan. Does this component do exactly what was described?
   No extra features, no missing features?
   - **Pass:** continue to Stage 2
   - **Fail:** rebuild the component against the plan before continuing

4. **Stage 2 — Prototype Quality Check:**
   Does the component render and function correctly? Can the SME interact with it?
   - **Pass:** mark component complete, move to next
   - **Fail:** fix and re-check

5. **Mark component complete** — only after both stages pass

### Component Status Handling

Focused assistants report one of these statuses:

**DONE:** Proceed to Stage 1 Spec Alignment Review.

**DONE_WITH_CONCERNS:** The assistant completed the work but flagged doubts. Read the
concerns before reviewing. If they affect correctness or scope, address them first.
If they are observations, note them and proceed to review.

**NEEDS_CONTEXT:** The assistant needs information not provided. Supply the missing
context and re-dispatch.

**BLOCKED:** The assistant cannot complete the component. Assess:
1. If it is a context problem, provide more context and re-dispatch
2. If the component is too complex, break it into smaller pieces
3. If the Discovery Plan is unclear, stop and clarify with the SME

## Two-Stage Review Detail

### Stage 1: Spec Alignment Review

The goal: does this component match what the SME approved?

Check:
- Does it do exactly what the Discovery Plan described for this component?
- Is there anything EXTRA that was not in the plan?
- Is there anything MISSING that was in the plan?

If any check fails: the assistant rebuilds before moving to Stage 2.

### Stage 2: Prototype Quality Check

The goal: does this component actually work?

Check:
- Does it render without errors?
- Can the SME click through it, fill in fields, and see realistic responses?
- Does it connect correctly to adjacent components already built?

If any check fails: the assistant fixes before marking complete.

## After All Components

Once all components pass both review stages:

1. Invite the SME to click through the full prototype
2. Ask them to validate each business flow against what they described in the Discovery Plan
3. Capture their observations for the documentation phase

Announce:
> "Your prototype is ready. Please click through it and let me know if everything
> works the way you described. We'll capture any surprises for the next step."

## Key Principles

- One component at a time — never build multiple in parallel
- Fresh assistant per component — no shared context between components
- Both review stages required — skipping either means the work is not complete
- The Discovery Plan is the source of truth — not your judgment about what would be useful
- Stop and ask if anything in the Discovery Plan is unclear before building
