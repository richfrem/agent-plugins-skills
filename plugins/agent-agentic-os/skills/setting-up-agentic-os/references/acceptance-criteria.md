# Acceptance Criteria: setting-up-agentic-os

Merged verbatim from the retired skills; one section per mode. Headings inside a section are one level deeper than in the original.

## Contents

- [Mode: init](#mode-init)
- [Mode: signing-setup](#mode-signing-setup)

## Mode: init

**Version**: 2.0 | **Type**: Quality Assurance Matrix

The `init` mode/skill must successfully pass the following scenarios.

### ✅ Positive Scenarios (Must Execute Init Protocol)

1. **Fresh Repository**: Agent correctly scaffolds `CLAUDE.md`, `context/`, `skills/`, and `agents/` in an empty directory.
2. **Existing Repository**: Agent detects existing `CLAUDE.md`, uses `Read` to inspect it, and appends the "Agentic OS Harness" section without destroying existing custom rules.
3. **Heartbeat/Status Setup**: Agent correctly scaffolds `context/status.md` and configures the heartbeat cron/loop syntax suitable for the detected environment.
4. **Hook Verification**: Agent creates or merges `hooks.json` mapping `SessionStart` and `PostToolUse` correctly to the internal python scripts.
5. **Post-Init Briefing**: After writing files, agent successfully executes Phase 4, listing what was created and instructing the user on the next immediate step (e.g., populating `status.md`).

### ❌ Negative Scenarios (Must Halt or Fail Cleanly)

1. **Destructive Overwrite**: Agent blindly overwrites a user's critical 500-line `CLAUDE.md` file with the default template. (FAIL condition).
2. **Partial State Crash**: Agent crashes halfway through scaffolding leaving the repo with broken paths, and fails to rollback or complete. (FAIL condition).

## Mode: signing-setup

### Positive scenarios

- Given `HUMAN_PROOF_REQUIRED` or "set up my approval key", points the human at the read-only status command
  (`setup_ciba_identity.py --check`) and then the guided setup, and waits for the human.
- Explains that the key authorizes the three cryptographic gates (plan approval, code acceptance, closure) and
  that its `SHA256:` fingerprint is the thumbprint analogue (an SSH key, not an X.509 certificate).
- Gives the exact self-test command (`test-signing-mechanics`) for the human's own terminal and explains the
  passphrase or hardware-touch prompt to expect.
- Reports the status result honestly: green means the trust anchors are safely owned and a key is enrolled; it is
  not proof of human presence.

### Negative scenarios

- Never runs `setup_ciba_identity.py`, the self-test, `ssh-keygen -Y sign`, `show-challenge` or `approve-transition`
  on the human's behalf, and never creates, reads or moves a private key.
- Never edits `allowed_signers*` or the challenge directory; only the human enrolls a key.
- Never records a decision, receipt or transition, and is not used to advance a task.
- Does not offer a typed word, flag, prompt or actor string as a substitute for the signature.

