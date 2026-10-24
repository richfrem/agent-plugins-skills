# Setup healthcheck and validation

The checklist that proves `init` left a working pipeline: the SQLite control plane, the instruction files, the git guards, and both identities. Run it after `init` or `--retrofit`, after cloning a project, and after `apm update`. For ongoing liveness (event bus, locks, memory) use the `health` mode of the `running-control-plane` skill; this reference is the setup half.

## Contents

- [How to run it](#how-to-run-it)
- [The checklist](#the-checklist)
- [What a healthy fresh setup looks like](#what-a-healthy-fresh-setup-looks-like)
- [Proving it works](#proving-it-works)
- [When a check fails](#when-a-check-fails)

## How to run it

Run each command from the project root, using the skills as installed in the project (for example `.claude/skills/running-control-plane/` and `.claude/skills/setting-up-agentic-os/`; global installs have the same layout under the user folder). The two skills must sit side by side. Commands are written below as `<control>` (the `running-control-plane` skill folder), `<setup>` (the `setting-up-agentic-os` skill folder) and `<project>` (the repository).

## The checklist

| # | Check | Command | Healthy result |
|---|---|---|---|
| 1 | The SQLite pipeline and the required substrates | `python3 <control>/scripts/control_plane/installation_probe.py --target <project>` | `{"state": "COMPLETE", "missing": []}` |
| 2 | Instruction files: `AGENTS.md` is canonical, `CLAUDE.md` is a short pointer | `head -5 <project>/CLAUDE.md` | a few lines that point to `AGENTS.md` |
| 3 | The required files exist | the four `test -f` commands in [init-detailed-reference.md](init-detailed-reference.md), Phase 5 | four `OK` lines |
| 4 | The git guards are installed, wired and current, and the mode is declared | `python3 <control>/scripts/control_plane_mode.py status --target <project>` | `Control plane: ENABLED`, both guards `script_present, script_executable, wired`, `RESULT: consistent` |
| 5 | The agent's own identity (simulation key) | the checks in [agent-identity.md](agent-identity.md) | `simulation.ready: true`, one registered fingerprint matching the key file |
| 6 | The human's signing identity | `python3 <setup>/scripts/setup_ciba_identity.py --check --repo-root <project>` | exit `0` once the human has set it up; exit `1` and `NOT set up` on a fresh agent-run `init` |
| 7 | A simulation reaches DONE under the agent's key | see [Proving it works](#proving-it-works) | three signed gate rows |

Notes on the results:
- **Check 1** opens `context/control_plane.db` read-only. It checks the substrate files, the schema version, the transition table against the source state graph, and the transition trigger. `PARTIAL` lists what is missing.
- **Check 4** reports a guard as `stale` when the copy in `.git/hooks` was stamped for a different install location, for example after `apm update` or after moving the skill. Run it from the installed skill that wrote the guards, or refresh them with the `mode` workflow's `enable --yes`.
- **Check 6** is human-only to fix. The agent only reads the exit code; it never runs key creation (see the `signing-setup` mode).

## What a healthy fresh setup looks like

After an agent-run `init` with no tty, the correct state is:

| Part | State |
|---|---|
| Pipeline database and substrates | complete |
| Guards and mode | consistent, enabled |
| Agent simulation identity | ready |
| Human identity | **not ready**: only the human can fix it |
| Isolation of the agent from the human's trust files | **not ready** until a separate agent account is set up |

`init` creates the same 23 files as the original `init` did on an identical fresh repository (instruction files, `context/`, the database, the simulation identity, `wiki/`, the evolution-guard workflow and traces folder, and the generated documents). A human-not-ready result is expected, not a failure.

## Proving it works

The checks above show the pieces exist. A simulation shows they work together. Run the full simulation in the `simulator` mode of `running-control-plane` (section "Full run as the human approver"). A healthy run ends in DONE and leaves three rows in `signed_gate_evidence`, for APPROVED, VERIFY_EXIT and DONE, signed by `test-human@local` with the agent's simulation key:

```bash
sqlite3 <dir>/simulation_control_plane.db "select request_id,from_state,to_state,principal,fingerprint from signed_gate_evidence"
python3 <control>/scripts/agent_control.py --db-path <dir>/simulation_control_plane.db status --task-id <task-id>
```

## When a check fails

| Failing check | Fix |
|---|---|
| 1 reports `PARTIAL` or `MISSING` | re-run `python3 <setup>/scripts/init_agentic_os.py --target <project> --retrofit` |
| 1 reports a schema or transition mismatch | the database is from another version; follow the rebuild procedure in the `running-control-plane` skill (`control-plane-rebuild-recovery`) |
| 4 reports a guard missing or not wired | `python3 <control>/scripts/control_plane_mode.py enable --yes` |
| 4 reports `stale` | run `enable --yes` from the currently installed skill |
| 5 reports simulation not ready | create the identity as described in [agent-identity.md](agent-identity.md) |
| 6 exits 1 | ask the human to run `setup_ciba_identity.py` in their own terminal |
| 7 stops at `HUMAN_PROOF_REQUIRED` | the simulation database is not named `simulation_control_plane.db` |
| 7 refuses with `main_clean_before_approval` | commit the project and keep the simulation database outside the tree |

Remediation for failed initialization is also in [fallback-tree.md](fallback-tree.md), section "Mode: init".
