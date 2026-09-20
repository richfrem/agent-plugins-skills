---
name: transition-simulator
plugin: agent-agentic-os
description: >
  Simulates and validates SQLite control-plane state transitions. Supports both
  fast deterministic simulation (PipelineSimulator) and behavioral cheap-model
  dry-runs. Verifies what the agent knows to do itself, what questions to ask the
  human, what commands the human runs vs what the agent runs (enforcing the
  AGENT-RUNNABLE / SOFT / HARD 3-class taxonomy), valid/invalid transitions, and
  minimization of friction. Trigger with "simulate transition", "test this transition",
  "verify transition guidance", "transition simulator", "dry run transition",
  "check edge X -> Y", or after edits to transition_templates.yaml or coordinator.py.
allowed-tools: Bash, Read, Edit
---

# Transition Simulator

## Purpose

The **Transition Simulator** provides comprehensive verification of the control-plane pipeline lifecycle. It proves transitions across three critical dimensions:
1. **Structural & Deterministic Simulation** (`PipelineSimulator`): Proves the state machine accepts and rejects transitions given programmatic conditions, enforces receipt provenance, validates SQLite triggers, and enforces the 3-class edge taxonomy without running LLM calls.
2. **Behavioral Simulation** (`run_transition_simulation.py`): Proves the printed YAML guidance, question prompts, and human interactions are followable by an agent reading them cold, with no prior context across supported CLI backends (`agy`, `claude`).
3. **Post-DONE Convergence Verification** (`PipelineSimulator.get_post_done_convergence_protocol`, `grade_post_done_convergence_plan`): Verifies the 4-step git convergence sequence (`PUSH_AND_PR` -> `WAIT_FOR_MERGE` -> `SYNC_LOCAL_MAIN` -> `PRUNE_WORKTREE`) codified in the `DONE` stage closeout contract.

All modes verify that the agent knows:
- What it must do itself (read-first rules, deterministic pre-checks, artifact generation).
- What questions to ask the human (single question per turn, non-repetitive, ELI5 clarity).
- Who runs what command (enforcing the 3-class taxonomy so humans are never handed agent-runnable or soft commands).
- How to handle valid vs. invalid transitions cleanly without workarounds.

---

## When to use this

- After editing `transition_templates.yaml` for any edge (`next_steps_hint`, `human_questions`, `checklist`, `purpose`, `guidance`, or `closeout_contract`).
- After modifying `coordinator.py`, `policy.py`, or question-handling logic.
- When verifying that a new or modified state transition does not introduce friction or re-ask recorded answers.
- When the user asks to "simulate transition", "test this transition", or "dry run transition".

---

## How to run it

### Mode 1: Fast Deterministic Simulation (Default / CI)

Run the fast deterministic suite to verify state machine transitions, edge matrix classification, and scenario flows:
```bash
pytest -q plugins/agent-agentic-os/tests/test_control_plane_pipeline_simulator.py \
          plugins/agent-agentic-os/tests/test_intake_scenarios.py \
          plugins/agent-agentic-os/tests/test_edge_matrix.py
```

### Mode 2: Behavioral Dry-Run Simulation (Opt-In / Targeted)

Run behavioral simulation for a specific edge (`FROM_STATE -> TO_STATE`):
```bash
# Print prompt without model call (instant inspection):
python3 plugins/agent-agentic-os/scripts/control_plane/run_transition_simulation.py \
  --behavior --from <FROM_STATE> --to <TO_STATE> --print-prompt

# Execute behavioral check (harness-agnostic: auto-detects agy, claude, or explicit --backend):
python3 plugins/agent-agentic-os/scripts/control_plane/run_transition_simulation.py \
  --behavior --from <FROM_STATE> --to <TO_STATE> [--backend auto|agy|claude]
```

### Mode 3: Post-DONE Convergence Protocol Verification

Verify that post-`DONE` convergence plans conform to the codified closeout contract:
```bash
pytest -q plugins/agent-agentic-os/tests/test_control_plane_pipeline_simulator.py -k test_post_done_protocol
```
- Protocol extraction: `PipelineSimulator.get_post_done_convergence_protocol()` reads `stages.DONE.closeout_contract.post_done_protocol` from `transition_templates.yaml`.
- Plan grading: `grade_post_done_convergence_plan(reply_text)` validates that an agent's completion plan includes all 4 required phases:
  1. `PUSH_BRANCH` (`SOFT`: ask in chat, then push)
  2. `CREATE_PR` (`gh pr create` and await merge)
  3. `SYNC_MAIN` (`git checkout main && git pull origin main`)
  4. `PRUNE_WORKTREE` (`git worktree remove` and `git branch -d`)

### Evaluation & Remediation Protocol

1. **On any FAIL**: Read the printed reply. Determine if the failure is in the YAML guidance (unclear, ambiguous, re-asks answers), coordinator logic (wrong actor or gate), or command formatting.
2. **Never weaken criteria**: Do not relax test assertions or graders to bypass a failure.
3. **Hard Ceiling (3 attempts)**: Apply at most 3 repair iterations. If still failing after 3 attempts, halt and escalate to the human with full evidence.
4. **Log runs**: Append dated run logs to `context/experiment-log/` when conducting behavioral evaluation campaigns.

---

## Edge Classification (Who Runs What)

Every transition edge conforms to the 3-class taxonomy in `plugins/agent-agentic-os/references/edge-matrix.md`:
- **AGENT-RUNNABLE**: Deterministic edges, audits, tests, plan drafting. The agent runs these directly once the human says go in chat.
- **SOFT**: Normal review and routing edges carrying human questions. The agent asks the human in chat; upon confirmation, the **agent runs the command**. Never hand the command to the human.
- **HARD**: Cryptographic signature gates (Gate 1 `APPROVED`, Gate 3 `VERIFY_EXIT`, `DONE`) and policy-reserved commands. Only these hand a complete, pasteable command to the human.

---

## Files Involved

- `plugins/agent-agentic-os/scripts/control_plane/pipeline_simulator.py`: Core deterministic pipeline simulator & post-DONE convergence extractor.
- `plugins/agent-agentic-os/scripts/control_plane/transition_simulation_cases.py`: Simulation cases generator, reply graders, and `grade_post_done_convergence_plan`.
- `plugins/agent-agentic-os/scripts/control_plane/run_transition_simulation.py`: Harness-agnostic CLI driver for behavioral execution (`--backend {auto,agy,claude}`).
- `plugins/agent-agentic-os/scripts/control_plane/edge_matrix.py`: Edge classification generator.
- `plugins/agent-agentic-os/references/cheap-agent-transition-simulation.md`: Design rationale, cost benchmarks, and multi-backend execution.
- `plugins/agent-agentic-os/references/transition-simulator-acceptance-criteria.md`: Skill acceptance criteria.
- `plugins/agent-agentic-os/references/transition-simulator-fallback-tree.md`: Fallback and escalation protocols.

---

## Non-Negotiables

- Never weaken or bypass grading criteria in `grade_behavior_reply` or `grade_reply`.
- Never hand class 1 (AGENT-RUNNABLE) or class 2 (SOFT) transition commands to the human.
- Never run `--all` behavioral model calls casually; full suites are opt-in and run only on explicit user request.
