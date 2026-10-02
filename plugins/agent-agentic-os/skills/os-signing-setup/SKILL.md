---
name: os-signing-setup
plugin: agent-agentic-os
description: >
  Guide a human through creating the SSH signing key that authorizes the human approval gates (plan approval, code acceptance, closure):
  passphrase-protected key or FIDO hardware key, the allowed_signers files, the isolation
  status, and the interactive signing self-test, on macOS or Windows. Trigger with "set up my
  approval key", "create the ssh signing key", "set up signing identity", "HUMAN_PROOF_REQUIRED",
  "test my signing key". Never used to record decisions or advance tasks.
allowed-tools: Bash, Read
---

# OS Signing Setup (`os-signing-setup`)

Guides human operators through creating and verifying passphrase-protected or FIDO hardware SSH signing keys required for cryptographic approval gates (`APPROVED`, `VERIFY_EXIT`, `DONE`).

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Never Run Setup Autonomously**: Key creation and self-tests require interactive human terminal prompts; agents must never run them directly.
2. **Never Touch Private Keys**: Never create, read, copy, or move private keys, and never edit `allowed_signers*`.
3. **No Automated Approvals**: Never pipe passphrases or fabricate signatures; signatures are proof of actual human presence.

## Quick start

Check signing status and key readiness:

```bash
python3 scripts/setup_ciba_identity.py --check
```

## Workflow

1. **Check Status**: Run status check to verify whether trust anchors or keys are missing.
2. **Guide Key Creation**: Provide instructions for the human to run `python3 scripts/setup_ciba_identity.py` in their own terminal.
3. **Run Self-Test**: Direct the human to execute `python3 scripts/test_signing_mechanics.py`.
4. **Inspect Results**: Advise the human based on script output and verify readiness.

## Verification

Confirm trust anchors exist and key is verified (exit code 0):

```bash
python3 scripts/setup_ciba_identity.py --check
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for cryptographic approval workflows.
- [fallback-tree.md](references/fallback-tree.md) — Remediation pathways when signing checks fail.
- [isolation-setup.md](references/isolation-setup.md) — OS account isolation steps and residual risk notes.
- [os-signing-setup-guide.md](references/os-signing-setup-guide.md) — Plain-language setup guide and identity definitions.
- [SIGNING_WORKFLOW_OVERVIEW.md](references/SIGNING_WORKFLOW_OVERVIEW.md) — Cryptographic boundary architecture.
