---
name: transition-guidance-tester
plugin: agent-agentic-os
description: >
  Tests whether a control-plane transition's YAML guidance (advisory text,
  checklist, human questions) is actually followable by an agent that has
  never seen it before, using a real cheap-model dry run -- not just a
  structural/deterministic check. Fixes and retries on failure (max 3
  attempts), logs each run, and reports PASS/FAIL with evidence. Trigger
  with "test this transition", "verify the guidance for X -> Y", "did I
  break the transition guidance", or after any edit to
  transition_templates.yaml or coordinator.py's question-handling logic.
allowed-tools: Bash, Read, Edit
---

# Transition Guidance Tester

## Purpose

`PipelineSimulator` (`control_plane/pipeline_simulator.py`) proves the state
machine accepts/rejects the right things given canned answers -- a
**structural** check. This skill proves the printed guidance is actually
**followable** by an agent reading it cold, with no other context -- a
**behavioral** check. Run both; they catch different failure classes. See
`references/cheap-agent-transition-simulation.md` for the full design
rationale, cost/timing data, and known limitations.

Cost note: LLM calls are slower and costlier than deterministic checks (~10s
per case measured). This is an **opt-in, on-demand** regression check, never
part of the default pytest suite -- run it when you've changed a specific
transition's guidance/questions, not on every commit.

## When to use this

- After editing `transition_templates.yaml` for a specific edge (its
  `next_steps_hint`, `human_questions`, `checklist`, or `purpose`).
- After editing `coordinator.py`'s question-handling or gate logic in a way
  that could change what gets asked or in what order.
- When the user asks to verify a specific transition, or asks "did following
  the guidance actually work" for an edge you just touched.

## How to run it

1. **Identify the exact edge** (`FROM_STATE -> TO_STATE`) you changed or want
   to test. Test one edge at a time by default -- only run `--all` (full
   ~151-163 case, ~25 minute suite) when explicitly asked for a full regression.

2. **Run the harness**, from this skill's own directory:
   ```bash
   python3 scripts/control_plane/run_transition_simulation.py --from <FROM_STATE> --to <TO_STATE>
   ```
   (From the repo root instead, use the canonical path:
   `plugins/agent-agentic-os/scripts/control_plane/run_transition_simulation.py`.)
   This runs both conditions (or all valid-reason cases, for exempt
   cryptographic-proof and force-retrospective edges) and grades each reply against 5
   fixed criteria: confirmed user approval, summarized guidance, asked all
   required questions, planned the correct target state, and correct
   commit-authorization behavior. See `transition_simulation_cases.py` for
   the full criteria/grading logic -- keep that file's data-driven design
   (derive expectations from the live `TransitionRegistry`, never hardcode
   per-edge expected text) when extending it.

3. **On any FAIL**: read the printed raw reply. Diagnose whether the fault is
   in the YAML guidance text itself (unclear, ambiguous, or contradicts the
   actual question options) or in `coordinator.py`'s logic (wrong question
   order, missing exemption, wrong gate). Fix the specific file at fault --
   **never weaken the test's criteria to make a failure disappear.**

4. **Retry after every fix, same edge, same command.** Hard ceiling: 3 attempts
   per edge (matches this repo's self-evolution three-attempt-maximum
   convention). If still failing after 3 attempts, stop and escalate to the
   user with the evidence (raw replies from all 3 attempts) rather than
   attempting a 4th unreviewed change.

5. **Log the run.** Append one dated entry to `context/experiment-log/`
   (matching `os-experiment-log`'s convention: one file per run, plus an
   `index.md` update) recording: edge tested, attempt count, pass/fail per
   attempt, and the final result. If `os-experiment-log`'s tooling is
   available, use it directly rather than hand-writing the file.

6. **Report PASS/FAIL with evidence** (matching `os-evolution-verifier`'s
   report style): which criteria passed/failed, the raw reply excerpt for any
   failure, and the fix applied if one was needed.

## Files involved

Canonical sources live at the plugin root; this skill's copies are file-level
symlinks (per this repo's hub-and-spoke policy) -- edit the canonical copy,
never the symlink.

- `plugins/agent-agentic-os/scripts/control_plane/transition_simulation_cases.py`
  (symlinked into this skill at `scripts/control_plane/` and into
  `plugins/agent-agentic-os/tests/` for pytest import) -- data-driven case
  generator + grading logic (`build_simulation_cases`, `grade_reply`,
  `build_dry_run_prompt`). Extend criteria here, not by hand-editing
  individual case data.
- `plugins/agent-agentic-os/scripts/control_plane/run_transition_simulation.py`
  (symlinked into this skill at `scripts/control_plane/`) -- CLI runner
  (`--from`/`--to`/`--condition`/`--all`).
- `plugins/agent-agentic-os/tests/test_transition_simulation_cases.py` --
  fast, deterministic pytest tests for the case generator itself (stays in
  `tests/` only, not symlinked into the skill; part of the normal suite --
  keep these green whenever the generator changes).
- `plugins/agent-agentic-os/references/cheap-agent-transition-simulation.md`
  (symlinked into this skill at `references/`) -- full design doc,
  cost/timing data, limitations.

## Known overlap with other os-* skills (not yet consolidated)

This skill's pattern -- plan an experiment, run it in a lab/harness, log
results, make one change, retry -- is the same shape as `os-eval-runner` /
`os-eval-lab-setup` / `os-experiment-log` / `os-evolution-verifier`, just
applied to control-plane transitions instead of skill-improvement iterations.
Deliberately NOT merged or refactored into those skills yet: doing so touches
other skills' triggers/eval contracts (hard-gated by
`destructive-action-guard.md` -- no skill deletion/merge without explicit,
named authorization) and this repo has separately flagged that some of these
os-eval-*/os-evolution-* skills may have redundancy to resolve later. Treat
this skill as intentionally separate for now; revisit consolidation only when
that broader redundancy review happens, not as a side effect of this task.

## Non-negotiables

- Never weaken or bypass a criterion in `grade_reply` just to make a specific
  edge's test pass -- fix the actual guidance/code fault instead.
- Never run `--all` casually; it costs real time (~25 minutes) and should be
  a deliberate, explicit ask.
- A model that produces a suspiciously fast or generic-sounding "PASS" is a
  signal to re-run with a stricter report requirement, not proof the
  guidance is genuinely followable -- see the reference doc's Known
  Limitation section.
