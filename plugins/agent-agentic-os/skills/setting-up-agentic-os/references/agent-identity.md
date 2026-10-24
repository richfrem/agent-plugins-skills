# The agent's own identity and key

The Agentic OS gives the agent a signing identity of its own, separate from the human's. The human signs real work with their own key and passphrase. The agent signs **simulations** with its own key, so it can run the pipeline end to end, verify the setup, and make improvements without a human present. Creating and checking this identity is part of setup validation and of the healthcheck.

## Contents

- [Two identities, kept apart](#two-identities-kept-apart)
- [Creating it](#creating-it)
- [Validating it (healthcheck)](#validating-it-healthcheck)
- [Proving it works](#proving-it-works)
- [Boundaries](#boundaries)
- [When something is not ready](#when-something-is-not-ready)

## Two identities, kept apart

| | Human identity | Agent simulation identity |
|---|---|---|
| Used for | Real work: `context/control_plane.db` | Simulations: `simulation_control_plane.db` |
| Key | the human's, passphrase-protected, created by the human (`signing-setup` mode) | `context/simulation/identity/simulation_key`, passphrase-less by design |
| Trust file | `context/identity/allowed_signers` | `context/simulation/identity/allowed_signers` |
| Principal | the human's | `test-human@local` |
| Namespace | `control-plane@agentic-os.local` | `control-plane@agentic-os.local` |
| Who may create it | only the human | the agent |

A key enrolled as a simulation key is refused on real work, even if someone relabels it as a human key in the production trust file. The simulation identity can never approve real work.

## Creating it

`init` creates it by default, in both fresh and retrofit mode. The agent may also create or reuse it on demand (run from this skill's folder; the project is the current repository):

```bash
python3 -c "
import sys; sys.path.insert(0, '../running-control-plane/scripts')
from pathlib import Path
from control_plane.simulation_identity import ensure_simulation_identity
ensure_simulation_identity(Path('<project-path>'))"
```

It is safe to repeat: it reuses the key and only ever adds enrollment lines. Skip it with `init_agentic_os.py --no-simulation-identity`. The simulator also creates the key next to a simulation database on first use.

What it writes, all under `<project>/context/simulation/identity/`:

| File | Mode | Purpose |
|---|---|---|
| `simulation_key` | 0600 | the agent's private key |
| `simulation_key.pub` | 0644 | its public half |
| `allowed_signers` | 0600 | trust file: the key enrolled as `test-human@local` |
| `allowed_signers_selftest` | 0600 | trust file for the self-test namespace |
| `challenges/` | 0700 | working folder for the challenge being signed |

## Validating it (healthcheck)

Run these from this skill's folder against the project. Together they are the setup validation.

**1. All three identity parts, reported separately** (human approval, simulation, isolation):

```bash
python3 -c "
import sys, json
sys.path.insert(0, '../running-control-plane/scripts')
from pathlib import Path
from control_plane.simulation_identity import dual_identity_status
print(json.dumps(dual_identity_status(Path('<project-path>')), indent=2, default=str))"
```

Read it like this:

| Part | Healthy | What it means when not |
|---|---|---|
| `simulation.ready` | `true`, one registered fingerprint | the agent cannot run simulations yet; create the identity |
| `human.ready` | `true` once the human has run `setup_ciba_identity.py` | normal on a fresh setup: only the human can fix it |
| `isolation.ready` | `true` when the agent runs as a separate account | `false` with "account exists" means the account exists but its runtime and file permissions are not verified |

A fresh agent-run `init` normally reports simulation **ready**, human **not ready**, isolation **not ready**. That is expected: the agent never creates the human's key.

**2. The key matches its trust file:**

```bash
ssh-keygen -lf <project-path>/context/simulation/identity/simulation_key.pub
```

The `SHA256:` fingerprint must equal the one `dual_identity_status` lists under `simulation.keys`.

**3. The pipeline's SQLite database and substrates are complete:**

```bash
python3 ../running-control-plane/scripts/control_plane/installation_probe.py --target <project-path>
```

Expected: `{"state": "COMPLETE", "missing": []}`. It checks the substrate files, the schema version, the transition table against the source state graph, and the transition trigger.

**4. Permissions:** the identity folder is 0700, the private key and trust files are 0600.

## Proving it works

Validation says the pieces exist; a simulation proves they work. Run the full simulation in the `simulator` mode of `running-control-plane` (its `simulator` reference, section "Full run as the human approver"). A healthy run reaches DONE and leaves three rows in `signed_gate_evidence` (APPROVED, VERIFY_EXIT, DONE) signed by `test-human@local` with the simulation key's fingerprint:

```bash
sqlite3 <dir>/simulation_control_plane.db "select request_id,from_state,to_state,principal,fingerprint from signed_gate_evidence"
```

Verified on 2026-10-23: 12 states, 25 transition decisions, 12 verification receipts, three signed gates, all with the agent's own key.

## Boundaries

- Never use the simulation key for real work, and never point a simulation at `context/control_plane.db`; the simulator refuses.
- The agent never creates, reads or copies the human's key, never edits `context/identity/allowed_signers*`, and never fabricates a human signature or confirmation.
- The key is passphrase-less on purpose: it can only ever approve simulations.

## When something is not ready

| Symptom | Fix |
|---|---|
| `simulation.ready` is `false` | run the creation command above |
| A simulation stops at `HUMAN_PROOF_REQUIRED` | the database is not named `simulation_control_plane.db`, so no signer was chosen |
| Gate 1 refuses with `main_clean_before_approval` | the source checkout has uncommitted paths; commit them and keep the simulation database outside the tree |
| `installation_probe` says `PARTIAL` | re-run `init_agentic_os.py --target <path> --retrofit` |
| Fingerprints differ | the trust file and key are out of step; delete `context/simulation/identity/` and recreate it (simulation only; never touches the human's identity) |
