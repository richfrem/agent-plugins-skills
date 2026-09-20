# Signing workflow overview (Gate 1 human approval)

Gate 1 (`AWAITING_APPROVAL -> APPROVED`) is approved by a signature from an SSH key only the human holds.
This is the full first-time sequence. Everything except the status check is run by the human, in their own terminal.
Paths are relative to the skill folder (`scripts/...`) or the plugin (`agent_control.py`).

| # | Step | Command | Writes |
|---|---|---|---|
| 0 | Prerequisites | check OpenSSH; decide where the passphrase lives | nothing |
| 1 | Create the key and enroll it | `python3 scripts/setup_ciba_identity.py` | `~/.ssh/agentic-os_signing`, `context/identity/` |
| 2 | Check status | `python3 scripts/setup_ciba_identity.py --check` | nothing |
| 3 | Mechanics self-test | `python3 scripts/test_signing_mechanics.py` | temporary files, removed |
| 4 | Approve a gate | `show-challenge`, `ssh-keygen -Y sign`, `approve-transition` | the approval, in one transaction |

Already set up (or after an upgrade)? Start at step 2: the status check tells you what, if anything, to redo.

## 0. Prerequisites
- **OpenSSH 8.1+** (`ssh-keygen -V` or `ssh -V`). macOS and Linux ship it; Windows 10/11 ships OpenSSH, and FIDO hardware keys need
  Win32-OpenSSH 8.9+. The setup refuses if SSHSIG support is missing.
- **A passphrase you will keep somewhere safe** (a password manager is fine). Setup refuses a software key without one.
  The passphrase is typed only at the `ssh-keygen` prompt; never give it to an agent or to these scripts' arguments.
- **Optional but recommended: a separate account for the agent** (`agentic-os-local-agent`). Setup prints the administrator
  commands (macOS `sysadminctl`, Windows `net user`, Linux `useradd`) and never runs them. Without it the agent runs as you and can
  reach your files; see the honest limits below and `references/isolation-setup.md`.

## 1. Create the key and enroll it
Run `python3 scripts/setup_ciba_identity.py` from the repository (it must be a terminal, as you, not the agent account).
1. It checks OpenSSH and, if an identity from an older version exists, migrates it (`[MIGRATED] n allowed_signers line(s) ...`).
2. **Key:** creates `~/.ssh/agentic-os_signing` and asks you for a passphrase twice, or reuses it (`[REUSE] ... already exists`).
   Use `--type ecdsa-sk` for a FIDO hardware key (you touch it instead), `--key PATH` for another location, `--force` to add a
   second key without removing the first. A key with no passphrase is refused and, if it was just created, removed.
3. **Identity folder:** creates `context/identity/` (mode 0700) with `challenges/` (0700), `allowed_signers` (0600) and a separate
   `allowed_signers_selftest` (0600).
4. **Enroll:** adds your public key to both files, prints its `SHA256:` fingerprint, and says `already enrolled` on a repeat run.
5. **Isolation:** reports any `[TODO]` (for example the agent account does not exist) and prints, never runs, the account commands.
6. It offers the self-test; answering `y` only prints the command, so run step 3 yourself.

## 2. Check status (read-only)
`python3 scripts/setup_ciba_identity.py --check`. Exit code 0 = ready, 1 = not ready.
- Ready: `Signing identity status: ready`, then `enrolled keys: 1`, the principal, key type and `SHA256:` fingerprint.
- Not ready: `Signing identity status: NOT set up` followed by `missing/unsafe:` lines, such as `LEGACY_NAMESPACE` (an old bare
  namespace; re-run step 1), wrong file modes, or a folder the agent could write.

## 3. Mechanics self-test
`python3 scripts/test_signing_mechanics.py` (also `agent_control.py test-signing-mechanics`). Signs a throwaway challenge with your
key (passphrase prompt or touch), verifies it against `allowed_signers_selftest`, and removes the files. Expected:
`Signature verified: principal ..., ED25519 key SHA256:..., namespace control-plane-selftest@agentic-os.local.` and
`Confirmed: this self-test signature cannot be used as an approval`. `context/identity/challenges/` is empty afterwards.

## 4. Approve a gate
1. The agent runs `coordinate-transition --task-id <id> --to APPROVED`. It stops with `HUMAN_PROOF_REQUIRED` and a `request_id`;
   a PENDING `transition_request` is stored.
2. You run `agent_control.py show-challenge --request-id N`. It writes the exact challenge bytes to `context/identity/challenges/`,
   prints them (read them: this text is the approval) and prints the `ssh-keygen -Y sign -f <key> -n control-plane@agentic-os.local <file>`
   command.
3. You run that command and enter your passphrase (or touch the key). It writes `<file>.sig`.
4. You run `agent_control.py approve-transition --request-id N`. Expected: `Approved: AWAITING_APPROVAL -> APPROVED (transition ...),
   signature verified.` Signature check, one-time consumption, the human decision rows and the state change happen in one
   transaction; any failure leaves the task in `AWAITING_APPROVAL`.

There is no separate signing script: signing is the standard `ssh-keygen -Y sign` command printed in step 2 of this flow, so the
signing code path is OpenSSH's, not ours.

## Security boundaries
- **Passphrase required** (or a hardware key). See step 0.
- **Trust anchors** live in `context/identity/` and are human-owned: `allowed_signers` (production) and `allowed_signers_selftest`,
  mode 0600, folder 0700. Enrolling a key is what lets its signature approve, so the agent must never edit them, and the isolation
  check fails when the agent account can write them.
- **Namespace isolation.** Production signatures use `control-plane@agentic-os.local`; the self-test uses
  `control-plane-selftest@agentic-os.local`, verified against a different file. A self-test signature can never approve a task, and a
  signature under the old bare `control-plane` namespace never verifies.
- **Bound to the exact content.** The challenge binds the task, the edge, the spec and plan content hash, the current occupancy, a
  nonce and an expiry; changed content, a stale or reused request, or another key's signature is refused.
- **Honest limits.** If the agent runs as your own account it can still reach your files and the database; real isolation needs the
  separate agent account. Not yet bound: policy version, key revocation lists, re-verification at later gates (see
  `references/map-debt.md`).

### Plain English Security Intuition
- **Private key** (`~/.ssh/agentic-os_signing`): the secret that makes your signature. The file is encrypted with your personal
  passphrase, so an agent that opens or copies the file sees only scrambled data. Without the passphrase it cannot read the secret or
  forge a signature. That protection is only as strong as the passphrase (use a long one) and only holds while the passphrase stays
  with you: never give it to an agent, and keep it out of anything the agent can read.
- **Public key** (the line in `allowed_signers`): safe to show to everyone, including the agent. Think of it as a photo of your
  signature on file: it lets the system check that a signature came from you, but it cannot be used to create one.
- **What actually needs guarding** is not who can see the public key but who can change the `allowed_signers` file: an agent that
  could add its own public key there could approve as itself. That is why the file is human-owned (0600) in a folder the agent
  cannot write, and why the isolation check fails when it can.
