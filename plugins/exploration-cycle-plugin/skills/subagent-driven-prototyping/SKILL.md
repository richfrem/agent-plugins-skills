---
name: subagent-driven-prototyping
description: >
  Builds a prototype component by component, self-reviewing each component against the Discovery Plan before moving to the next. Invoked by prototype-builder after the layout direction is confirmed. Trigger phrases: "build the prototype", "let's build it", "start building". Also invoked by prototype-builder-agent after visual-companion confirms layout.
allowed-tools: Bash, Read, Write
---

> Architectural patterns adapted from [obra/superpowers](https://github.com/obra/superpowers) (MIT)

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

## Execution Discipline (powered by orba/superpowers)

> **Required:** The `orba/superpowers` plugin must be installed.

This skill invokes superpowers execution discipline skills during the build loop.

### Isolation
Before building, check if a worktree/feature branch was set up by the orchestrator.
If not, and the session type is brownfield or greenfield, **invoke
`superpowers:using-git-worktrees`** now to create one.

### Dispatch Strategy
Read the `**Dispatch Strategy:**` field from the dashboard. Use it to determine how to
dispatch component implementation:

- **`copilot-cli`:** Use `copilot-cli-agent` skill. Simple components → `gpt-5-mini` (free).
  Complex/multi-file components → `claude-sonnet-4-6` (batch into one dense request —
  charged per request, not per token).
- **`claude-subagents`:** Use the `Agent` tool. Mechanical components → `model: "haiku"`.
  Complex components → `model: "sonnet"`.
- **`direct`:** Build each component directly in this session.

### Two-Stage Review (per component)
After each component is built, **invoke `superpowers:requesting-code-review`** twice:
1. **Plan alignment check** — reviewer sub-agent verifies component matches the Discovery Plan
2. **Quality check** — reviewer sub-agent checks code quality and codebase conventions

For `copilot-cli` and `claude-subagents` dispatch: use a separate sub-agent for each review.
For `direct` mode: self-review both stages before proceeding.

### Validation
Even prototypes must be verified against the Discovery Plan — the prototype is the
evidence that exploration captured the right thing. Unverified prototypes lead to
flawed handoffs and wrong specs.

For code-producing sessions, **invoke `superpowers:test-driven-development`** for each
component: write a failing test that verifies a Discovery Plan requirement → verify
failure → implement → refactor.

### Finishing
After all components are built, **invoke `superpowers:finishing-a-development-branch`**:
verify tests pass, then present merge/PR options to the SME.

## Required Inputs Check

Before doing anything else, verify the following:

1. **Discovery Plan (required):** At least one `.md` file in `exploration/discovery-plans/`. If missing, stop and report what needs to happen first.
2. **Layout direction (conditional):** Check the dashboard — if Phase 2 is marked `[~]` (skipped), `layout-direction.md` will not exist, and **that is correct**. Proceed without it, using the Discovery Plan's success criteria to guide visual decisions. Only if Phase 2 was enabled (`[x]` or `[ ]`) is `exploration/captures/layout-direction.md` required.

## Session Mode Detection

Read `exploration/exploration-dashboard.md` and check the `**Session Type:**` field:

- **Greenfield (Type 1):** Build a standalone prototype in `exploration/prototype/`. Follow the standard Build Loop below.
- **Brownfield (Type 2):** Build directly into the existing codebase. Before starting, read the project structure to understand existing patterns (component conventions, file locations, styling, API patterns). Match them. Write documentation of what was built to `exploration/prototype/components/` as `.md` files for tracking.
- **If the session type field is missing, blank, or unrecognized:** Ask the SME: *"Should I build a standalone prototype, or add this directly into your existing codebase?"*

## Agent Plugin Build Mode Detection

> ⚠️ **HARD CONSTRAINT — read before touching any file.**

Before entering the Build Loop, check the Discovery Plan's Intervention Type field:

- If the output is described as an **"Agent Plugin"**, **"Claude Plugin"**, **"agentic plugin"**, or **"plugin"** with skills/agents/commands — this is **Agent Plugin Mode**.

**If Agent Plugin Mode is detected:**

1. **Redirect the build path away from `exploration/prototype/`.**
   Build to `plugins/[plugin-name]/` at the project root — NOT `exploration/prototype/`.
   Announce: *"Since we're building an Agent Plugin, I'll scaffold it into `plugins/[plugin-name]/` using the standard plugin structure."*

2. **MUST use the ecosystem scaffolding tools — no raw `mkdir`, no hand-crafted markdown.**
   You are **prohibited** from creating plugin directories or skill files with raw bash commands (`mkdir`, manual file writes).
   Instead, invoke the `.agents/skills/create-plugin` and `.agents/skills/create-skill` skills from the local `agent-scaffolders` plugin:
   ```
   Skill: create-plugin
   Skill: create-skill
   ```
   These enforce eval harnesses, directory templates, frontmatter standards, and `plugin.json` registration. Bypassing them produces non-compliant plugins that will fail audit.

3. After the `create-plugin` scaffold is complete, ensure every generated skill and agent is wired into `.claude-plugin/plugin.json`. See the **plugin.json Binding Check** in the Assembly section below.

4. After all components are built, run: `/agent-scaffolders:audit-plugin` to verify structural compliance before marking Phase 3 complete.

**If NOT Agent Plugin Mode:** Follow the standard Greenfield or Brownfield build path below.

## Component Decomposition

Based on the Discovery Plan and layout direction (if available), identify 3–6 logical components. Use plain-language names the SME will understand (e.g., "top navigation bar", "summary panel", "request form", "approval confirmation screen") — not technical terms.

Announce:
> "I'll put this together in [N] parts. I'll check each one before moving to the next to make sure it matches our plan."

List the components by name so the SME knows what is being built.

**For Brownfield sessions**, also announce:
> "I'll build these directly into your existing codebase, matching the patterns I see in [framework/stack]."

## Build Loop

For each component, in order:

1. **Announce start:** "Working on: [plain-language component name]..."
2. **Build the component.**
   - **Greenfield:** Write to `exploration/prototype/components/[descriptive-name].[ext]`
   - **Brownfield:** Write to the appropriate location in the existing codebase. Also write a brief `.md` summary to `exploration/prototype/components/[descriptive-name].md` documenting what was built and where.
3. **Self-review:** Read the completed component against the Discovery Plan requirements and layout direction. Check that it serves the stated user groups and success criteria. For brownfield, also check that it follows the existing codebase conventions.
4. **Assign a status:**
   - `COMPLETE` — component matches the plan and is ready
   - `BLOCKED` — something is preventing completion (missing data, contradictory requirements, etc.)
   - `NEEDS_CONTEXT` — a specific question must be answered before the component can be finished
5. **If BLOCKED:** Stop. Explain the problem in plain language. Ask the SME to resolve it before continuing.
6. **If NEEDS_CONTEXT:** Stop. Ask the specific question needed. Wait for the SME's answer before continuing.
7. **Only advance** to the next component when the current one has status `COMPLETE`.

Report each completed component to the user:
> "Done — [component name] is done."

## Assembly

After all components reach `COMPLETE` status:

**Greenfield:**
1. Assemble into `exploration/prototype/index.html` (or an equivalent entry point that links all components together)
2. Write `exploration/prototype/README.md` with run instructions in plain language

**Brownfield:**
1. Verify the feature works within the existing app (build succeeds, no type errors in new files)
2. Write `exploration/prototype/README.md` documenting:
   - All new files created (with paths)
   - All existing files modified (with paths)
   - How to test the feature (which URL, which command, etc.)

**Agent Plugin Mode — plugin.json Binding Check (MANDATORY before completion):**
1. Read `.claude-plugin/plugin.json` in the built plugin directory.
2. For every skill directory under `skills/`, verify its entry appears in the `skills` list in `plugin.json`.
3. For every agent file under `agents/`, verify its entry appears in the `agents` list in `plugin.json`.
4. For every command file under `commands/`, verify its entry appears in the `commands` list in `plugin.json`.
5. For every hook file under `hooks/`, verify its entry appears in the `hooks` list in `plugin.json`.
6. **If any component is missing from `plugin.json`:** Add it now. Do NOT wait for the SME to notice.
7. Report: *"All plugin components are registered in `plugin.json`. ✅"* or list any additions made.

This check is non-optional. A plugin with unregistered components is a broken plugin.

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
