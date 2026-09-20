# Gate 1 signing identity: isolation setup

Gate 1 (`AWAITING_APPROVAL -> APPROVED`) advances only when a human's SSH key signs a challenge and
the signature verifies against `allowed_signers`. This page explains the setup, the modes, and, just as
important, what this does **not** protect against.

## What the human does (macOS, Windows, Linux)
1. `python3 plugins/agent-agentic-os/scripts/setup_ciba_identity.py` creates a passphrase-protected SSH
   key (or a FIDO hardware key with `--type ecdsa-sk`), the `context/identity/` folder, and enrolls the key.
   Use `--check` for a read-only status and `--force` to add another key (old keys stay enrolled).
2. `python3 plugins/agent-agentic-os/scripts/agent_control.py test-signing-mechanics` proves the passphrase
   prompt or hardware touch works, against a separate self-test file. It is never an approval.
3. At Gate 1, the agent runs `coordinate-transition --to APPROVED`, which returns `HUMAN_PROOF_REQUIRED` and a
   request id. The human then runs `agent_control.py show-challenge --request-id N`, signs the printed text
   with the printed `ssh-keygen -Y sign` command, and runs `agent_control.py approve-transition --request-id N`.
   There is no `--signature` argument: the signature path is derived from the request.

The key is an SSH key, not an X.509 certificate. Its `SHA256:` fingerprint plays the role of a certificate
thumbprint. Windows 10/11 ships OpenSSH (FIDO keys need Win32-OpenSSH 8.9+, other platforms OpenSSH 8.2+).

## What is protected, and how
| Item | Path | Mode | Purpose |
|---|---|---|---|
| Production trust anchor | `context/identity/allowed_signers` | 0600, human-owned | namespace `control-plane` only |
| Self-test trust anchor | `context/identity/allowed_signers_selftest` | 0600, human-owned | namespace `control-plane-selftest@agentic-os.local`; never read by approvals |
| Challenge directory | `context/identity/challenges/` | 0700, human-owned | per-request challenge and signature files |
| Private signing key | your own `~/.ssh` | 0600 | never stored in the repo, never shared |

Gate 1 refuses to proceed unless these are owned by the human, not writable by the agent account, free of
symlinks, and the verifying process is not the agent. The SQLite database is deliberately not part of this
check: the agent must keep writing it for ordinary transitions.

## Ranked ways to separate the agent from your keys
1. **Container or devcontainer (recommended).** The agent runs in a container with only the repository
   mounted, with no access to your host `~/.ssh`, sockets or IPC. You approve on the host.
2. **Dedicated OS account.** Create the unprivileged `agentic-os-local-agent` account and run the agent as
   that account. The setup script prints the administrator commands for macOS, Windows and Linux; it never
   runs them.
3. **Same-account exclusion (weakest, interim only).** If the agent must share your account, unset
   `SSH_AUTH_SOCK` for it and keep the files above owner-only. This is not a substitute for 1 or 2.

## Mode
- **strict (the only mode).** No prompt, piped input, injected input function, `--answers`, flag or actor string
  can authorize the cryptographic gates (APPROVED, VERIFY_EXIT, DONE). Only a verified OpenSSH signature can.
  A missing, invalid or symlinked policy file means strict, and so does one that asks for a mode that no longer
  exists: the earlier interactive-prompt fallback was removed and a policy file requesting it is reported and
  ignored. In a same-account setup the agent can still edit files it can write; see the residual risk below.

## Residual risk (read this)
- A **same-account agent** that writes the SQLite database directly, or edits the coordinator code, can bypass
  the signing hook. The signature check protects the coordinator path against an agent that lacks your keys
  and against scripted answers; it does not stop a determined process with your privileges. Only a separate
  process or account (a broker) closes that, which is out of scope here.
- **No trusted display.** A hardware touch proves you touched the token, not that you understood the request.
  `show-challenge` prints the exact bytes you sign; read them.
- **Not supported:** macOS **Touch ID** as a signing factor (OpenSSH cannot use it natively; it needs a
  Secure Enclave key provider), and SSH or X.509 **certificate** authorities. Both would be separate designs.
- File modes and ownership checks are POSIX. On Windows follow the account and folder-permission steps by hand;
  automated tests do not cover Windows.

## For the agent
Do not run the setup or the self-test, never create or read a private key, never edit `allowed_signers*`,
and never answer a passphrase or touch prompt. Give the human the exact commands and wait.
