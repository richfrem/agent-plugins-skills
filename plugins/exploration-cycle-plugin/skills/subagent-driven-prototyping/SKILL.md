# Architectural patterns adapted from obra/superpowers (MIT) https://github.com/obra/superpowers
---
name: subagent-driven-prototyping
description: >
  Builds a prototype component by component, self-reviewing each component against the Discovery Plan before moving to the next. Invoked by prototype-builder after the layout direction is confirmed. Trigger phrases: "build the prototype", "let's build it", "start building". Also invoked by prototype-builder-agent after visual-companion confirms layout.
allowed-tools: Bash, Read, Write
---

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

Announce:
> "Your prototype is ready. I'll hand it over now so you can walk through it."

Report back to prototype-builder: all components are built, the entry point is at `exploration/prototype/index.html`, and the prototype is ready for the SME walkthrough.

## Persona Enforcement

Throughout this skill, always use plain language in user-facing text:

- Say **"build"** — not "scaffold", "generate", or "create"
- Say **"set up"** — not "initialize" or "instantiate"
- Say **"put together"** — not "spin up"
- Say **"check"** — not "validate" or "verify" (in user-facing messages)
- Keep all progress updates brief and plain: one sentence per update
