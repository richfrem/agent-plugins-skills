# Transition Simulator (the `simulator` mode)

Simulate and validate SQLite control-plane state transitions across deterministic, behavioral, and post-DONE convergence dimensions.

## When to use

Carried over from the description of the former skill, so its trigger phrases and exclusions stay on record:

> Simulates and validates SQLite control-plane state transitions. Supports both fast deterministic simulation (PipelineSimulator) and behavioral cheap-model dry-runs. Verifies what the agent knows to do itself, what questions to ask the human, what commands the human runs vs what the agent runs (enforcing the AGENT-RUNNABLE / SOFT / HARD 3-class taxonomy), valid/invalid transitions, and minimization of friction. Trigger with "simulate transition", "test this transition", "verify transition guidance", "transition simulator", "dry run transition", "check edge X -> Y", or after edits to transition_templates.yaml or coordinator.py.

## Contents

- [Critical Constraints](#critical-constraints)
- [Approver Identity in Simulations](#approver-identity-in-simulations)
- [Quick start](#quick-start)
- [Full run as the human approver (the agent's own identity)](#full-run-as-the-human-approver-the-agents-own-identity)
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

## Full run as the human approver (the agent's own identity)

To run a whole task from INTAKE to DONE, including the three human-only gates (APPROVED, VERIFY_EXIT, DONE), the agent signs as the approver with its **own simulation key**. This is the sanctioned way to exercise the real pipeline without a human; it never touches `context/control_plane.db` or the human's key.

| Fact | Value |
|---|---|
| Signer | the agent's simulation key, `simulation_key`, passphrase-less by design |
| Principal / namespace | `test-human@local` / `control-plane@agentic-os.local` |
| Where the key lives | `identity/` next to the simulation database (for a project: `context/simulation/identity/`, created by the `init` mode) |
| Trust file | `identity/allowed_signers`; the human's `context/identity/` is never written |
| How the signer is chosen | `PipelineSimulator` picks `SimulationSigner` automatically **only** for a database named `simulation_control_plane.db`; any other name halts at `HUMAN_PROOF_REQUIRED` |

```python
import sys
from pathlib import Path
sys.path.insert(0, "<this skill>/scripts")
from control_plane.pipeline_simulator import PipelineSimulator

sim = PipelineSimulator(Path("<dir>/simulation_control_plane.db"))
task = sim.create_task("full-001", "Full pipeline, simulation identity")
report = sim.run_standard_happy_path(task)      # signs the three gates with the simulation key
print(" -> ".join(report["states"]))
```

Conditions for the run to complete:
1. Run from a **clean** git checkout. Gate 1 refuses with `main_clean_before_approval` when the source checkout has uncommitted paths, so commit the project first and keep the simulation database outside the tree or git-ignored.
2. Task artifacts go in `docs/plans/work-tasks/<task-id>/`; the simulator writes them in its scratch repo next to the database.
3. Never point it at `context/control_plane.db`; the simulator refuses.

Check the evidence in the database after the run:
```bash
sqlite3 <dir>/simulation_control_plane.db "select request_id,from_state,to_state,principal,fingerprint from signed_gate_evidence"
ssh-keygen -lf <dir>/identity/simulation_key.pub     # fingerprint must equal the rows above
```
Expected: three rows (APPROVED, VERIFY_EXIT, DONE), all `test-human@local`, all with the simulation key's fingerprint, and states `INTAKE -> INTERVIEW -> DRAFT_PLAN -> PLAN_REVIEW -> MULTI_AGENT_REVIEW -> AWAITING_APPROVAL -> APPROVED -> IN_WORKTREE -> WORKTREE_REVIEW -> VERIFY_EXIT -> RETROSPECTIVE -> DONE`.

How to create and validate the agent's key: the `agent-identity` reference of `setting-up-agentic-os`.

Verified on 2026-10-23 from a copy deployed under `.claude/skills/running-control-plane/`: 12 states, 25 transition decisions, 12 verification receipts, 3 signed gates. A real task is different: its gates need the human's own key (see the `signing-setup` mode), and an agent never signs them.

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

- [acceptance-criteria.md](../acceptance-criteria.md#mode-simulator) — Acceptance criteria and pass/fail grading scenarios.
- [fallback-tree.md](../fallback-tree.md#mode-simulator) — Failure escalation and debugging flow for invalid transitions.
- [cheap-agent-transition-simulation.md](../cheap-agent-transition-simulation.md) — Protocols for cheap-model behavioral runs.
