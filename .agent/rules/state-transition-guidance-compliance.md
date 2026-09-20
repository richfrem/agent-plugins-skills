---
description: >
  Mandatory compliance rule for agents driving SQLite-control-plane state transitions
  (work-intake and equivalent pipelines). Exists because agents, including Claude, have
  repeatedly skipped or self-answered YAML transition guidance instead of following it
  literally.
globs: ["**/*"]
---

# State Transition Guidance Compliance

## The Failure Pattern This Rule Targets

Agents driving a control-plane pipeline (work-intake, self-evolution, or
equivalent) have a documented, repeated failure mode: treating the YAML
transition guidance (`transition_templates.yaml`'s `human_questions`,
`next_steps_hint`, `stage_question_ids`) as advisory prose to summarize,
rather than as literal, mandatory input to follow exactly.

Concretely observed failure instances (see `references/map-debt.md` for full
detail, not repeated here):

- A full task cycle (`issue-593-context-overhead`) skipped `DRAFT_PLAN` and
  `AWAITING_APPROVAL` entirely, never produced a spec artifact, and closed
  with a human retrospective recorded verbatim as "a complete failure."
- Mid-session, an agent piped a default/recommended answer into an
  interactive human-approval prompt instead of asking the human for their
  actual answer first, requiring the human to explicitly stop and say
  "follow questions at each transition."
- An agent pushed a branch to a remote origin without an explicit, isolated
  push instruction from the human, misreading "remove X from GitHub origin"
  as implicit push authorization.
- An agent made a sequence of unilateral remediation decisions (reverting
  files, moving directories, restoring symlinks) after discovering damage
  from an unauthorized bulk edit, without pausing to present the plan and
  get confirmation before acting, despite already having been corrected for
  this exact pattern earlier in the same session.
- At `APPROVED -> IN_WORKTREE`, the transition guidance literally said
  "create or select an isolated feature worktree and branch, record both
  with update-worktree." The agent instead registered the main checkout
  itself as the worktree path via `update-worktree --path "$(pwd)"`,
  never creating an isolated `.worktrees/task-<id>/` directory at all —
  not a tooling gap, a direct failure to do what the instruction said.
- The same pipeline's own `create_task()` computes a `main_dirty_advisory`
  field (dirty file count/paths) that the skill's own instructions require
  reporting to the user immediately if `dirty_count > 0`, recommending a
  commit before `APPROVED` so interim work doesn't accumulate uncommitted
  through the whole planning phase. The agent never reported it — partly
  because the CLI `init` subcommand discards `create_task()`'s return value
  and never prints the advisory (a real tooling gap), and partly because the
  agent also never independently checked `git status` to compensate, despite
  the instruction not depending on the CLI surfacing it.

## The Rule

1. **A YAML `human_questions` entry is not optional summary material — it is
   the literal question to ask, verbatim or near-verbatim, and the literal
   set of accepted answers to record.** Do not infer, default, or
   self-answer on the human's behalf, even when a "Recommended" option
   exists. A recommended default is a suggestion to present, not a license
   to select it without asking.
2. **`next_steps_hint` and `denial_message` text describes the actual
   required sequence, not a paraphrase to work around.** If the hint says to
   run a specific command with a specific flag, run that command with that
   flag. If it says to create an isolated worktree, create an isolated
   worktree — do not substitute an equivalent-seeming shortcut, such as
   registering the main checkout itself as if it were the worktree.
3. **When a step's own documented output includes an advisory or field the
   instructions say to report** (e.g. `main_dirty_advisory`), and the CLI or
   tool you're calling doesn't surface it, do not treat that as license to
   skip the check. Call the underlying function directly, or independently
   verify the same condition (e.g. `git status`), so the instruction is
   satisfied regardless of a tooling gap. Report the tooling gap separately
   as its own friction/map-debt item — it does not excuse skipping the step.
4. **After discovering damage, corruption, or an unauthorized action** (by
   yourself or by direct instruction), do not proceed through a multi-step
   remediation unilaterally. Present the audit (what's broken, why, proposed
   fix) and get explicit confirmation before executing each remediation step
   that isn't purely read-only verification (diagnose commands, test runs,
   `git status`/`git diff` are fine to run freely; `git mv`, file reverts,
   and `restore`-style mutating commands are not).
5. **A single correction from the human on this pattern does not
   self-resolve for the rest of the session.** If corrected once for
   skipping or self-answering a transition question, treat every subsequent
   transition in the same session with the same heightened literalness —
   do not regress after a few exchanges.
6. **When in doubt about whether an action is "just verification" or "a
   decision,"** treat it as a decision requiring confirmation. The bar for
   "just running a read-only check" is narrower than it feels in the moment.

## Non-Negotiables

- Never pipe a canned or default answer into an `--interactive` control-plane
  prompt without having first obtained that exact answer from the human in
  this conversation.
- Never treat "the user mentioned X in passing" as equivalent to "the user
  gave an explicit, isolated instruction to do X" for any state-changing
  action (push, transition, deletion, rename).
- Never chain more than one non-reversible remediation action without an
  intermediate check-in, even when each individual action seems obviously
  correct in isolation.
- Never register the main checkout as a substitute for an isolated worktree
  when the transition guidance says to create one.
- Never let a documented advisory field go unreported solely because the CLI
  wrapper around it failed to print it — verify independently.

## Enforcement: the guidance-compliance gate (added 2026-09-14)

This rule is no longer advisory-only for `agent-agentic-os`'s control plane.
`TransitionCoordinator.coordinate_transition()` now asks a mandatory extra
question, `guidance_compliance_confirmation`, on every non-force-close
transition: "Have you read and followed this transition's YAML guidance
exactly?" It can ONLY be answered via a real `interactive=True` call with a
real human typing the answer — it can never be satisfied by
`provided_answers`/`--answers`, precisely to prevent an agent self-certifying
compliance on a human's behalf. A "NO," or any attempt to answer it
non-interactively, sets a permanent `guidance_block_reason` on the task,
refusing all further transitions, commits, and pushes until a human explicitly
runs `clear-guidance-block --human-confirmed ...`.

**Before changing any transition's YAML guidance or the coordinator's
question-handling logic**, use the `transition-simulator` skill
(`plugins/agent-agentic-os/skills/transition-simulator/`) to verify the
guidance is still followable by an agent reading it cold — run
`run_transition_simulation.py --from <STATE> --to <STATE>` for the specific
edge you changed. This is opt-in (costs real time via LLM calls), not part of
the default pytest suite.
