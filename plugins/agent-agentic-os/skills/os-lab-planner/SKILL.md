---
name: os-lab-planner
description: >
  Turns a confirmed improvement brief into an evidence-based plan: audits what already
  exists, chooses a path (orchestrate existing, update existing, or create new), brainstorms
  2-3 options with tradeoffs, then writes the task plan and a self-contained delegation
  prompt. Non-interactive: it works from the brief that os-lab-agent hands it and does not
  interview the user. Use when asked to "plan an improvement", "write a delegation prompt",
  "audit what exists before improving X", "should we update or create this skill", or when
  os-lab-agent has a confirmed brief. DO NOT USE to build the lab repo (os-lab-setup), run
  mutation iterations (os-lab-loop), score a change (os-lab-scorer), review or backport lab
  results (os-lab-backport), write run logs or charts (os-lab-log), or manage memory
  (os-lab-memory).
---

# OS Lab Planner

Receives a brief from `os-lab-agent` and produces a plan plus a delegation prompt. It never
asks the user open interview questions: if the brief lacks a target, goal or tool list, stop
and return the gap to `os-lab-agent`.

## Contents

- [Critical constraints](#critical-constraints)
- [Workflow](#workflow)
- [Routing and installed check](#routing-and-installed-check)
- [Output](#output)
- [References](#references)

## Critical constraints

1. **Read-only until the plan is written.** Steps 1 to 3 only read files.
2. **Verify before claiming.** Claim an existing skill or agent only after reading its file.
3. **2-3 options, always.** Never write a plan from a single approach.
4. **Skills are not created reactively.** Create only if the audit proves no existing skill
   can be extended, and the gap has recurred. Modify first.
5. **Never assume a CLI is available.** Use only the tools the brief lists as confirmed.
6. **Delegate, do not execute.** Dispatch goes through the matching `cli-agents` dispatcher
   skill (see [references/delegation.md](references/delegation.md)). Never call scripts
   owned by another plugin.

## Workflow

1. **Read the brief.** Needs: target, goal, success criteria, run depth, confirmed tools. If
   any is missing, stop and ask `os-lab-agent`.
2. **Audit what exists.** Read the target's source `SKILL.md` or agent file (not an installed
   copy), its evals, the target program file, and the latest results. Search for overlapping
   skills. Record the match quality (full, partial, none) and the gaps found. Use
   [references/audit-lenses.md](references/audit-lenses.md).
3. **Choose the path.** Use the table below. If a full, current match exists with no gaps,
   report "no action warranted" and stop.
   For **Update** or **Create**, register the work in the control plane before proposing it,
   then log the prior-art scan (read `references/map-debt.md` for `Repeat: YES` entries and
   `wiki/decisions/` for rejected approaches). Stop and escalate if a `Repeat: YES` entry
   matches the target.

   ```bash
   python3 scripts/agent_control.py init --task-id <slug> --title "<target>" --runtime os-lab-planner --task-type EVOLUTION
   python3 scripts/agent_control.py log-prior-art --task-id <slug> --summary "<what was reviewed>" --repeat-yes-entries "<csv or empty>"
   ```
4. **Brainstorm options.** Write 2-3 distinct approaches with effort and tradeoff, using the
   cheapest suitable tier from the `update-cli-models` skill in `cli-agents`. Put the audit
   gaps in the prompt. Give a recommendation. Template in
   [references/templates.md](references/templates.md).
5. **Write the plan and prompt.** Plan to `tasks/todo/<date>-<slug>-plan.md`; delegation
   prompt to `temp/delegation_prompt_<slug>.md`. Structural fixes come first, additive
   content after. The prompt must work cold: exact files, constraints, acceptance criteria.
6. **Hand back.** Return the plan path, prompt path, chosen option and the next skill. Do not
   dispatch until `os-lab-agent` confirms the user approved.

| Path | When | Next |
|---|---|---|
| Orchestrate | Capability exists and fits; the work is to run it | `os-lab-setup` then `os-lab-loop` |
| Update | Capability exists but has gaps | Delegate the plan, then `os-lab-setup` to validate |
| Create | Audit proves no existing capability | Scaffold with `create-skill` or `create-sub-agent`, a human reviews the evals, then `os-lab-setup` |

## Routing and installed check

Before naming any skill as the next step, verify it is installed in your active runtime harness (`.claude/skills/<name>`, `.agents/skills/<name>`, or global workstation profile via `apm list`). If it is missing or uninstalled,
stop and ask whether to install it (`apm install <pkg> [--skill <name>]`). Never route around a missing skill. Intent categories and
signal phrases: [references/routing-taxonomy.md](references/routing-taxonomy.md).

## Verification

Confirm the plan and prompt files exist and the handoff block has all seven fields.

## Output

Plan file, delegation prompt, and this block at the end:

```text
## HANDOFF_BLOCK
TARGET: <skill or agent name, or new:<description>>
PATH: <orchestrate | update | create | no-action>
OPTION: <chosen option name>
PLAN: <path>
PROMPT: <path>
NEXT_SKILL: <os-lab-setup | os-lab-loop | none>
STATUS: <ready | blocked>
```

## References

- [templates.md](references/templates.md) - brainstorm, plan and delegation prompt templates
- [audit-lenses.md](references/audit-lenses.md) - gap lenses and prior-art check
- [routing-taxonomy.md](references/routing-taxonomy.md) - intent categories and confidence
- [delegation.md](references/delegation.md) - how to hand the prompt to a CLI backend
