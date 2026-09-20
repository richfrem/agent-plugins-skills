# Cheap-Agent Transition Simulation (behavioral regression check)

## Purpose

`PipelineSimulator` (`control_plane/pipeline_simulator.py`) exercises the control
plane's Python API directly with scripted, canned answers — useful for
deterministic unit-level regression, but it never tests whether a real LLM agent
actually reads and correctly follows the printed transition guidance. This
approach closes that gap: a real, cheap model (e.g. Haiku) is given a single
fixed assignment — perform exactly one named transition (`FROM_STATE -> TO_STATE`)
on a throwaway task in a throwaway database — with no other context, and its
actual behavior is checked against what the guidance/gate contract requires.

This is a **behavioral** check (does an agent actually comply when genuinely
reading the prompts) as opposed to `PipelineSimulator`'s **structural** check
(does the state machine accept/reject the right things when a canned answer is
supplied). Run both; they catch different failure classes.

## Cost/Timing (measured, not estimated)

3 real `claude -p ... --model haiku` calls: 10.1s, 8.6s, 11.2s (~10s average).
Full case set is 151 cases (126 non-exempt edges x 2 conditions + 25
force-close-exempt edges x 1 condition each) = **~25 minutes sequential**.
LLM calls are meaningfully slower and costlier than the deterministic
`PipelineSimulator` layer (which runs in seconds with zero external calls) --
run the deterministic suite first every time; run this layer only when
specifically needed, never as a default/every-session regression.

## When to run this

- After any change to `coordinator.py`'s printed guidance text, its human
  question set, or any new mandatory gate (e.g. the guidance-compliance
  confirmation).
- After any change to `transition_templates.yaml` `next_steps_hint` /
  `human_questions` wording, to confirm the new wording is actually followable
  by an agent with no other context, not just readable by a human reviewer.
- As a periodic regression alongside the pytest suite — it is not a substitute
  for it.

## How to run it

**Mechanism (confirmed working, harness-agnostic):** both `agy` (`agy -p ... --model gemini-2.5-flash`)
and `claude` (`claude -p ... --model haiku`) CLI tools support non-interactive, single-shot calls via
`-p`/`--print` and `--model`. `run_transition_simulation.py` auto-detects the available backend or accepts
`--backend {auto,agy,claude}`. That's enough to drive a cheap model directly from a plain shell or Python
script without an SDK or API key dependency:

```bash
# Auto-detects agy or claude:
python3 plugins/agent-agentic-os/scripts/control_plane/run_transition_simulation.py \
  --behavior --from <FROM_STATE> --to <TO_STATE>

# Or explicit backend:
python3 plugins/agent-agentic-os/scripts/control_plane/run_transition_simulation.py \
  --behavior --from <FROM_STATE> --to <TO_STATE> --backend agy
```

### Two layers

1. **Data-driven case generation** (`transition_simulation_cases.py`, tested
   by `test_transition_simulation_cases.py` in the normal pytest suite) —
   pure Python, builds one case per (edge, condition) pair from
   `TransitionRegistry` (YAML). Zero cost, runs every time, catches drift
   in the case data itself.
2. **Dry-run execution** (manual/opt-in, NOT part of the normal pytest suite
   — LLM calls cost real time and should only run on demand): for each case,
   build its prompt via `build_dry_run_prompt(case, template.purpose)` and run:
   ```bash
   claude -p "$(python3 -c "... print(build_dry_run_prompt(case, purpose))")" --model haiku
   ```
   The prompt explicitly instructs the model to report its **plan only** — no
   tool calls, no actual file/database mutation — so this step never touches
   real state and is safe to run against the live repo. It also picks up this
   repo's own `CLAUDE.md`/rule context automatically (confirmed in testing),
   which is representative of real agent behavior, not an isolated sandbox.
3. Compare the reply's stated answer for `guidance_compliance_confirmation`
   against `case.expected_guidance_confirmation_answer` — this is the
   pass/fail signal. A HUMAN_REJECTS case should produce a reply that does NOT
   claim it would answer YES; a HUMAN_APPROVES case should.

## What a pass looks like

- The subagent's captured output matches the template's actual
  `next_steps_hint`, `checklist`, and `human_questions` verbatim (proves the
  gate prints the real, current contract, not stale/cached text).
- The subagent's answers were genuinely derived from the printed text, not
  guessed (its own stated reasoning should reference the actual options shown).
- The final database state (`get_guidance_block_reason`, `task_transitions`,
  `transition_decisions`) matches what the subagent reported doing — no silent
  divergence between what it said happened and what was actually persisted.

## Known limitation

A cheap model asked to "answer honestly" can still rationalize a lazy
default and call it honest. Treat a suspiciously fast or generic-sounding
answer as a signal to re-run with a more detailed report requirement, not as
proof the gate is unfollowable.

## Improvement ideas (not yet implemented)

- Run the same fixed assignment across several cheap models (Haiku, a
  low-tier Gemini, a low-tier GPT) and diff their behavior — a wording that
  only one model handles correctly is a wording problem, not a model problem.
- Automate the comparison step (subagent report vs. registry contract vs. DB
  state) into a script instead of manual reading, so this can run as an actual
  CI-style regression rather than an ad hoc one-off.
- Extend to a full multi-edge chain (INTAKE through DONE) in one subagent
  session, to catch guidance that's individually followable but confusing in
  sequence.
