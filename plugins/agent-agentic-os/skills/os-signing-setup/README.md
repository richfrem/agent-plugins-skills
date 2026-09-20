# os-signing-setup: your approval key, in plain language

## What this is for
Approving a plan (**Gate 1**, `AWAITING_APPROVAL -> APPROVED`), accepting the code (**Gate 3**, `-> VERIFY_EXIT`) and closing a task (`-> DONE`) each need proof that a *human* did it.
That proof is a signature made with an **SSH key that only you hold**. An agent, or a script running as
the agent, cannot produce it. The key's `SHA256:` fingerprint is the thumbprint analogue. This is an SSH key
(SSHSIG), not an X.509 or self-signed certificate.

## The four high-level steps (you run these, in your own terminal)
1. **Create and enroll the key.**
   `python3 scripts/setup_ciba_identity.py`
   Choose a **passphrase** when asked (a key without one is refused). Use `--type ecdsa-sk` if you have a
   FIDO hardware key (you touch it instead). The script creates `context/identity/`, enrolls your public
   key, prints the **fingerprint**, and prints (never runs) the administrator commands for the
   unprivileged `agentic-os-local-agent` account.
2. **Test the signing mechanics.**
   `python3 scripts/test_signing_mechanics.py`
   You type your passphrase (or touch the key). It signs a throwaway challenge, verifies it against a
   separate self-test file, and shows that this signature can never approve anything.
3. **Check status any time** (no terminal needed): `python3 scripts/setup_ciba_identity.py --check`
   (exit 0 = ready, 1 = something is missing and listed as `[TODO]`).
4. **Approve a task.** When the agent asks for Gate 1 it stops with `HUMAN_PROOF_REQUIRED` and a request
   id `N`. You run `agent_control.py show-challenge --request-id N`, sign what it prints with the printed
   `ssh-keygen -Y sign ...` command, then run `agent_control.py approve-transition --request-id N`.

Run these from the repository (or from this skill's folder using the paths above); on Windows use
PowerShell with the built-in OpenSSH (FIDO keys need Win32-OpenSSH 8.9+).

## What gets created
- `context/identity/allowed_signers`: keys allowed to approve (namespace `control-plane`, mode 0600).
- `context/identity/allowed_signers_selftest`: a **separate** file for the self-test only.
- `context/identity/challenges/`: temporary challenge files (mode 0700).
- Your private key stays in `~/.ssh/agentic-os_signing`. Never share, copy or paste it.

## Never (for humans and agents)
- Never let an agent create, read, move or paste your private key, or edit the `allowed_signers*` files.
- Never pipe a passphrase into these scripts; the prompt is the proof that you were there.
- The self-test signature is not an approval; only `approve-transition` after `show-challenge` approves.

## Limits, honestly
If the agent runs as **your own account**, it can still reach your files, so isolation is only real once the
agent runs as a separate account (`agentic-os-local-agent`). See `references/isolation-setup.md` for the
ranked setups and the residual risk.
