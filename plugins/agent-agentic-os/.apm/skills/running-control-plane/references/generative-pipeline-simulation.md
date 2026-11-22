# End-to-End Generative Roleplay Simulation Protocol

A live, cold-read end-to-end test of the control plane where **the parent agent plays the Human Operator** (using the agent's simulation signing key) and **a fresh subagent plays the Orchestrator** walking a real, bounded coding task through every state (`INTAKE -> DRAFT_PLAN -> PLAN_REVIEW -> APPROVED -> IN_WORKTREE -> WORKTREE_REVIEW -> VERIFY_EXIT -> DONE`) while logging every instruction, CLI, YAML, and gate-handoff friction point.

## Contents

- [Why This Tier Exists](#why-this-tier-exists)
- [Sandbox Setup (Zero Touch to Real Repo)](#sandbox-setup-zero-touch-to-real-repo)
- [Roleplay Execution Loop](#roleplay-execution-loop)
- [Signing Gates with the Simulation Key](#signing-gates-with-the-simulation-key)
- [Friction Log & Fix-Verify Loop](#friction-log--fix-verify-loop)

## Why This Tier Exists

`running-control-plane` uses three complementary simulation tiers:

1. **Deterministic (`PipelineSimulator`)** — fast Python unit/integration tests of DAG legality, SQLite triggers, and signing mechanics.
2. **Single-edge cheap-model behavioral (`run_transition_simulation.py`)** — cold-reads one edge at a time and grades `WHO_RUNS`, `COMMAND`, and `SAY` (see [cheap-agent-transition-simulation.md](cheap-agent-transition-simulation.md)).
3. **End-to-end generative roleplay (this protocol)** — catches multi-step UX, doc drift, blank prompts, missing CLI flags (`--db-path`), contradictory hints, and handoff dead-ends that unit tests and single-edge probes never see.

Run this protocol after any major state-machine, YAML, coordinator, or skill-doc change.

## Sandbox Setup (Zero Touch to Real Repo)

1. Create an isolated directory under the OS's **resolved** temp path (on macOS, `/private/tmp/sim-generative-<run>/`, NOT `/tmp/...` — `isolation_check` rejects symlink path components with `SYMLINK_COMPONENT`).
2. Copy the candidate `running-control-plane` and `orchestrating-agent-work` skill folders side-by-side into `<sandbox>/skills/` (matching APM's installed layout).
3. Initialize a clean git repository at `<sandbox>/repo` with a tiny module and passing unit test (e.g. `greeter.py` + `test_greeter.py`), committed on `main`. Include `context/simulation/` and `.worktrees/` in `.gitignore`.
4. Initialize `<sandbox>/repo/context/simulation/simulation_control_plane.db` (schema v15) and enroll a throwaway simulation signing key via `SimulationSigner(<sandbox>/repo/context/simulation/identity)`.
5. **Never** point the simulation at the real repository's `context/control_plane.db` or the human's `~/.ssh` keys.

## Roleplay Execution Loop

1. Launch a fresh subagent (ideally a lighter/faster model such as `flash` to expose unclear instructions) with a simple, concrete coding task (e.g., adding a 2-line function and unit test).
2. Give the subagent strict rules:
   - Work **only** inside `<sandbox>/repo` and `<sandbox>/repo/.worktrees/`.
   - Read and follow `<sandbox>/skills/running-control-plane/SKILL.md` cold.
   - Always pass `--db-path <sandbox>/repo/context/simulation/simulation_control_plane.db`.
   - **Never** run `show-challenge`, `ssh-keygen -Y sign`, `approve-transition`, or `SimulationSigner` itself; halt on `HUMAN_PROOF_REQUIRED` and hand the exact commands to the parent (Human Operator).
   - Walk every state in order (`INTAKE -> DRAFT_PLAN -> PLAN_REVIEW -> APPROVED -> IN_WORKTREE -> WORKTREE_REVIEW -> VERIFY_EXIT -> DONE`) without skipping.
   - Maintain a numbered **Friction & Instruction Issues Log** across every turn.
3. The parent agent plays the Human Operator: answers scoping questions, accepts the plan/diff, and signs all 3 cryptographic gates (`APPROVED`, `VERIFY_EXIT`, `DONE`) with the simulation key.

## Signing Gates with the Simulation Key

When the subagent halts on `HUMAN_PROOF_REQUIRED` and returns `request_id`:

```bash
env -u SSH_AUTH_SOCK PYTHONPATH="<sandbox>/skills/running-control-plane/scripts" <venv-python> -c '
from pathlib import Path
from agent_control import ControlPlane
from control_plane.simulation_identity import SimulationSigner

repo = Path("<sandbox>/repo").resolve()
cp = ControlPlane(db_path=repo / "context/simulation/simulation_control_plane.db")
cp.repo_root = repo
rec = SimulationSigner(repo / "context/simulation/identity")(cp, <request_id>)
print(rec.from_state, "->", rec.to_state, rec.transition_id)
'
```

Unsetting `SSH_AUTH_SOCK` (`env -u SSH_AUTH_SOCK`) satisfies `isolation_check`'s `SSH_AUTH_SOCK_SET` guard.

## Friction Log & Fix-Verify Loop

1. **Run 1**: Complete `INTAKE -> DONE` without editing any skill files mid-run. Report all friction findings to the human operator first.
2. **Fix**: Apply surgical fixes to YAML, scripts, wrappers, and docs in the task worktree; run deterministic tests.
3. **Run 2 (Verification)**: Spin up a **fresh** `<sandbox-2>` with the updated skills and a **fresh** cold subagent, repeat `INTAKE -> DONE`, and compare Run 1 vs Run 2 friction counts to prove the fixes worked.
