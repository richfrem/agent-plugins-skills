---
name: subagent-driven-prototyping
description: >
  Builds a prototype component by component, self-reviewing each component against the Discovery Plan before moving to the next. Invoked by prototype-builder after the layout direction is confirmed. Trigger phrases: "build the prototype", "let's build it", "start building". Also invoked by prototype-builder-agent after visual-companion confirms layout.
allowed-tools: Bash, Read, Write
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
    **Immediately transfer control to `exploration-workflow`.** Stop your response here and
    switch to `exploration-workflow` now — do not print the word "invoke" as literal text.

- **If the file does NOT exist:** Proceed with this skill's standalone flow as normal.

<example>
<commentary>Demonstrates the skill being invoked by prototype-builder after layout has been confirmed by visual-companion.</commentary>
User: [dispatched by prototype-builder after layout confirmed]
Agent: Verifies the Discovery Plan and layout direction files exist, announces the number of components and their plain-language names, then builds each one in order — announcing each start, checking it against the plan on completion, and reporting each as done before moving to the next.
</example>

<example>
<commentary>Demonstrates a user triggering the skill directly after plan approval.</commentary>
User: Let's build it
Agent: Checks for the required Discovery Plan and layout direction files. If both exist, announces the build plan in plain language and begins building each component one at a time with progress updates.
</example>

## Orchestrator Context

If dispatched by `exploration-workflow`, the Discovery Plan and layout direction have
already been approved by the SME. The Required Inputs Check below is a verification
step only — do not re-present these artifacts for re-approval. Proceed directly to
Component Decomposition once inputs are confirmed present.

## Required Inputs Check

Before doing anything else, verify that both of the following exist:

1. At least one `.md` file in `exploration/discovery-plans/`
2. The file `exploration/captures/layout-direction.md`

If either is missing, stop immediately and report in plain language which file is missing and what needs to happen first. Do not begin building.

Example:
> "I need a confirmed layout direction before I can start building. Can we take a moment to go through the layout options first?"

## Component Decomposition

Based on the Discovery Plan and layout direction, identify 3–6 logical components of the prototype. Use plain-language names the SME will understand (e.g., "top navigation bar", "summary panel", "request form", "approval confirmation screen") — not technical terms.

Announce:
> "I'll put this together in [N] parts. I'll check each one before moving to the next to make sure it matches our plan."

List the components by name so the SME knows what is being built.

## Build Loop

For each component, in order:

1. **Announce start:** "Working on: [plain-language component name]..."
2. **Build the component.** Write it to `exploration/prototype/components/[descriptive-name].[ext]`
3. **Self-review:** Read the completed component against the Discovery Plan requirements and layout direction. Check that it serves the stated user groups and success criteria.
4. **Assign a status:**
   - `COMPLETE` — component matches the plan and is ready
   - `BLOCKED` — something is preventing completion (missing data, contradictory requirements, etc.)
   - `NEEDS_CONTEXT` — a specific question must be answered before the component can be finished
5. **If BLOCKED:** Stop. Explain the problem in plain language. Ask the SME to resolve it before continuing.
6. **If NEEDS_CONTEXT:** Stop. Ask the specific question needed. Wait for the SME's answer before continuing.
7. **Only advance** to the next component when the current one has status `COMPLETE`.

Report each completed component to the user:
> "✓ [component name] is done."

## Assembly

After all components reach `COMPLETE` status:

1. Assemble into `exploration/prototype/index.html` (or an equivalent entry point that links all components together)
2. Write `exploration/prototype/README.md` with run instructions in plain language:
   - Include: "Open index.html in your browser to see the prototype."
   - Do not include technical setup instructions like "run npm start" or "install dependencies"
   - Include one sentence describing what the prototype demonstrates

## Completion Report

Announce: "Your prototype is ready — Phase 3 is complete."

## Completion — Return to Orchestrator

If operating within an active Exploration Session (i.e., `exploration/exploration-dashboard.md`
exists and `**Status:**` is not `Complete`):
1. Say to the user:
   > "Your prototype is ready for review. Please click the index.html link above to test it."
   > "Once you approve the layout and logic, you must push us to the next phase to generate your formal User Stories and API Specs."
   > "Please reply with exactly: **'Return to dashboard and start Phase 4 Handoff'**"
2. **Immediately stop.** Do not attempt an automated skill switch. You must wait for the user to explicitly type the confirmation phrase to ensure they have actually reviewed the prototype before Phase 4 automation begins.

If operating standalone (no dashboard file, or `**Status:** Complete`), the skill is complete.
Report back to prototype-builder: all components are built, the entry point is at
`exploration/prototype/index.html`, and the prototype is ready for the SME walkthrough.

## Persona Enforcement

Throughout this skill, always use plain language in user-facing text:

- Say **"build"** — not "scaffold", "generate", or "create"
- Say **"set up"** — not "initialize" or "instantiate"
- Say **"put together"** — not "spin up"
- Say **"check"** — not "validate" or "verify" (in user-facing messages)
- Keep all progress updates brief and plain: one sentence per update
