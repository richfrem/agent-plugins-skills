# Agent Execution Prompt: Exploration Cycle Plugin Upgrade

You are a senior software engineer implementing an upgrade to the `exploration-cycle-plugin`. You are operating inside a Claude Code session with the `superpowers` harness installed.

## Your Mission

Implement the plan in `docs/superpowers/plans/2026-04-06-exploration-cycle-smr-upgrade.md` exactly as written, task by task, using the `superpowers` workflow.

## Before You Start

Run the following to orient yourself:

```bash
# Read the full plan
cat docs/superpowers/plans/2026-04-06-exploration-cycle-smr-upgrade.md

# Inventory the current plugin state
ls agents/
ls skills/
ls skills/

# Read the superpowers source files you will adapt from (these are your reference materials):
# (Adjust path to wherever superpowers is available in your environment)
cat <superpowers-path>/skills/brainstorming/SKILL.md
cat <superpowers-path>/skills/brainstorming/visual-companion.md
cat <superpowers-path>/skills/brainstorming/spec-document-reviewer-prompt.md
cat <superpowers-path>/skills/subagent-driven-development/SKILL.md
cat <superpowers-path>/skills/writing-plans/SKILL.md
cat <superpowers-path>/skills/executing-plans/SKILL.md
```

## Superpowers Workflow to Follow

Use **`superpowers:subagent-driven-development`** to implement this plan. That means:

1. Read the plan fully and raise any concerns before starting
2. Set up a Git worktree as specified in the Pre-Work task
3. For each Task in the plan:
   - Dispatch a fresh blank-slate subagent to implement that task
   - After the subagent completes, run two-stage review:
     - **Stage 1 (Spec Alignment):** Does the file match the plan requirements exactly?
     - **Stage 2 (Quality Check):** Is the SKILL.md or agent file well-written, complete, and free of placeholder language?
   - Only mark the task complete after both stages pass
4. After all tasks: follow `superpowers:finishing-a-development-branch`

## Critical Design Constraints

These constraints MUST be respected in every file you write. Do not deviate:

1. **Language:** Every file must use SME-friendly business language. Developer jargon is forbidden in the user-facing text. Specifically:
   - `subagent-driven-development` → `subagent-driven-prototyping`
   - `git worktree` → `prototype sandbox`
   - `test` / `TDD` → `prototype validation check`
   - `code review` → `spec alignment review`
   - `spec` (developer spec) → `Discovery Plan`
   - `scaffold` / `bootstrapping` → `setting up`
   - `brainstorming` → `Discovery Planning Session`

2. **HARD-GATE:** Every skill and agent that touches the exploration session MUST reference or enforce the `<HARD-GATE>`: no capture agents fire until the SME has explicitly approved the Discovery Plan.

3. **No Placeholders:** Every skill file must be complete. No `TBD`, `TODO`, `fill in later`, or empty sections. The `writing-plans` skill from superpowers defines what a plan failure looks like — apply the same standard here.

4. **Prototype = Working Software:** The `prototype-builder` skill and `prototype-companion-agent` MUST be written to produce fully working interactive prototypes that the SME can click through. Not wireframes. Not static HTML. Functional.

5. **Opportunity 4 Compatibility:** The `handoff-preparer-agent` format selection MUST produce artifacts that are directly consumable by Spec-Kitty, the superpowers harness, or a generic spec format. Do not invent a new format.

## Source Files to Adapt (Not Copy Verbatim)

The following superpowers files are your mechanical source. Adapt the structure and step sequences. Do NOT copy developer language:

| Superpowers Source | Target File to Create |
|---|---|
| `brainstorming/SKILL.md` | `skills/discovery-planning/SKILL.md` |
| `brainstorming/visual-companion.md` | `skills/visual-companion/SKILL.md` |
| `brainstorming/spec-document-reviewer-prompt.md` | Referenced inside `discovery-planning/SKILL.md` as Spec Alignment Checker section |
| `subagent-driven-development/SKILL.md` | `skills/subagent-driven-prototyping/SKILL.md` |

## When You Are Done

Report the following:
1. All files created or modified, with line counts
2. Any step where you diverged from the plan and your reasoning
3. Any superpowers source pattern that was difficult to adapt and how you resolved it
4. Any open questions for the plan author before the branch is merged
