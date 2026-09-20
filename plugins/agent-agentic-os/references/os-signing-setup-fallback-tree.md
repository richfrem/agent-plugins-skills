# Fallback Tree: os-signing-setup

1. If `ssh-keygen` is missing or older than OpenSSH 8.1 (`SSH_KEYGEN_UNAVAILABLE` / `SSHSIG_UNSUPPORTED`), tell the
   human to install a current OpenSSH, then re-run `setup_ciba_identity.py --check`.
2. If the status reports `NO_ENROLLED_KEYS` or `NAMESPACE_MISMATCH`, tell the human to run
   `python3 scripts/setup_ciba_identity.py` in their own terminal; do not edit `allowed_signers*` for them.
3. If an isolation check fails (for example `SSH_AUTH_SOCK_SET`), explain the failure code from
   `references/isolation-setup.md` and have the human fix the environment; never bypass the preflight.
4. If the self-test or a signature is refused, show the refusal reason verbatim and have the human retry in a real
   terminal; a request that expired needs a fresh `coordinate-transition` request.
5. Never substitute a scripted, piped or agent-run step for the human's passphrase or key touch.
