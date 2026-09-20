---
name: os-signing-setup
plugin: agent-agentic-os
description: >
  Guide a human through creating the SSH signing key that authorizes the Gate 1 human approval:
  passphrase-protected key or FIDO hardware key, the allowed_signers files, the isolation
  status, and the interactive signing self-test, on macOS or Windows. Trigger with "set up my
  approval key", "create the ssh signing key", "set up signing identity", "HUMAN_PROOF_REQUIRED",
  "test my signing key". Never used to record decisions or advance tasks.
allowed-tools: Bash, Read
---

<example>
<commentary>The remediation error says the human has no signing key set up yet.</commentary>
user: "I got HUMAN_PROOF_REQUIRED and failed_checks lists missing files, what do I do?"
assistant: Points the human at the read-only status command, then the guided setup, and waits; never runs it.
</example>

<example>
<commentary>The human wants to prove the key works before an approval.</commentary>
user: "Test my signing key works."
assistant: Gives the exact self-test command for the human's own terminal and explains the prompt to expect.
</example>

# OS Signing Setup

## Purpose
The three human gates (Gate 1 `AWAITING_APPROVAL -> APPROVED`, Gate 3 `-> VERIFY_EXIT`, and closure `-> DONE`) each need a cryptographic approval from a human's SSH key. This
skill takes the human through creating that key and proving it works. The key is an **SSH key
(SSHSIG)**, not an X.509 certificate; its `SHA256:` fingerprint is the thumbprint analogue.

## Hard rules for the agent
1. **Never run the setup or the self-test yourself.** They are human tools: they refuse to run without a
   terminal and as the agent account. Give the human the exact commands and wait.
2. **Never create, copy, read or move a private key**, and never edit `allowed_signers*`. Enrolling a key
   is what lets a signature approve; only the human does it.
3. Never answer a passphrase or touch prompt, never pipe input into these scripts.

## When to use
- The remediation error `HUMAN_PROOF_REQUIRED` lists `failed_checks` or the human has no key yet.
- The human asks to set up, rotate (add another key) or test their approval key.
- Do NOT use it to approve a task (that is `show-challenge` / `approve-transition`), or for pipeline
  friction (map-debt, GitHub issues).

## Steps (the human runs these in their own terminal; paths are relative to this skill's folder)
1. Check status (read-only, no terminal needed):
   `python3 scripts/setup_ciba_identity.py --check`
   Exit 0 = ready, 1 = not ready (the output lists each `[TODO]`).
2. Guided setup (creates the key, enrolls it, prints account commands for the human to run):
   `python3 scripts/setup_ciba_identity.py`
   Add `--type ecdsa-sk` for a FIDO hardware key (touch); `--force` to add another key (old keys stay).
3. Prove it works (real passphrase prompt or touch, verified against the self-test file only):
   `python3 scripts/test_signing_mechanics.py`
   (The full plugin's `agent_control.py` exposes the same self-test as a verb.)
4. Use it: at Gate 1 the agent's `coordinate-transition --to APPROVED` returns `HUMAN_PROOF_REQUIRED` with
   a request id. The human runs `show-challenge --request-id N`, signs the printed challenge with the
   printed `ssh-keygen -Y sign` command, then runs `approve-transition --request-id N`
   (both are `agent_control.py` verbs in the full plugin).

## High-level flow for the agent
1. Detect the need (remediation error or the human asks). 2. Give the human the status command, then
the setup command, then the self-test command, one at a time, and wait for their pasted output.
3. Read the output only to advise (fingerprint present, `[TODO]` lines, exit codes); never act on their
behalf. 4. Point the human to `README.md` in this folder for the plain-language walkthrough.

## What it sets up
`context/identity/allowed_signers` (0600, namespace `control-plane@agentic-os.local`), a **separate**
`allowed_signers_selftest` (0600, namespace `control-plane-selftest@agentic-os.local`), and `challenges/` (0700). The
private key stays in the human's `~/.ssh`. The unprivileged agent account (`agentic-os-local-agent`) is
created by the human with the printed administrator commands; they are never run by the script.

## Cross-platform notes
macOS and Linux use the system OpenSSH; Windows 10/11 ships OpenSSH (FIDO needs Win32-OpenSSH 8.9+).
File modes are POSIX; on Windows follow the ownership steps in `references/isolation-setup.md`.

## References
- `references/SIGNING_WORKFLOW_OVERVIEW.md`: the full first-time sequence (prerequisites, create and enroll the key, status check, self-test, gate approval), expected output and security boundaries.
- `references/isolation-setup.md`: the full setup and the honest limits (same-account agents are not stopped).
