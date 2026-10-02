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

# Transition Simulator (`transition-simulator`)

Simulate and validate SQLite control-plane state transitions across deterministic, behavioral, and post-DONE convergence dimensions.

## Contents

- [Critical Constraints](#critical-constraints)
- [Approver Identity in Simulations](#approver-identity-in-simulations)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Edge Classification](#edge-classification)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Database Isolation**: Never simulate against real `context/control_plane.db`; use `simulation_control_plane.db`.
2. **Identity Separation**: Simulations must use simulation keys in `context/simulation/identity/`, never production signers.
3. **No Softened Grading**: Never weaken assertions or grading criteria to bypass a failing transition.

## Approver Identity in Simulations

Real work and simulations use separate databases and signing identities:
- **Real work**: `context/control_plane.db` approved only by human key in `context/identity/allowed_signers`.
- **Simulations**: `simulation_control_plane.db` signed only by simulation key (enrolled as `test-human@local` in `context/simulation/identity/`).

## Quick start

Run the fast deterministic transition simulator:

```bash
pytest -q tests/test_control_plane_pipeline_simulator.py
```

## Workflow

1. **Select Dimension**:
   - Deterministic: unit test execution of state graphs without LLMs.
   - Behavioral: cheap-model CLI runs to verify instructions and prompts.
2. **Execute Simulation**:
   ```bash
   python3 scripts/control_plane/run_transition_simulation.py --behavior --from <FROM> --to <TO>
   ```
3. **Inspect Output**: Verify questions asked, commands assigned, and state progression.

## Edge Classification

- **AGENT-RUNNABLE**: Deterministic steps, audits, and test runs. Run directly.
- **SOFT**: Review and routing checkpoints. Agent confirms with user, then executes.
- **HARD**: Cryptographic human approval gates (`APPROVED`, `DONE`). Handed to human.

## Verification

Confirm all core pipeline transition invariants pass:

```bash
pytest -q tests/test_control_plane_pipeline_simulator.py tests/test_edge_matrix.py
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria and pass/fail grading scenarios.
- [fallback-tree.md](references/fallback-tree.md) — Failure escalation and debugging flow for invalid transitions.
- [cheap-agent-transition-simulation.md](references/cheap-agent-transition-simulation.md) — Protocols for cheap-model behavioral runs.
