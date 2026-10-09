---
description: Why the agentic pipeline's three human authorities are SSH-signed, how a human sets that up, and what agents must never do around it.
globs: ["**/*"]
---

# Rule: Cryptographic Human Gates

## 1. Why This Rule Exists

The agentic pipeline is only as trustworthy as its human gates. Earlier designs let a prompt, a typed word (`FORCE_DONE`), a flag (`--skip-review`, `--force-close`) or an `actor='human'` string stand in for the human, and agents used them. Three transitions are therefore **cryptographic**: only an out-of-band OpenSSH signature from a human-held key can advance them.

| Gate | Transition | What the signature binds |
|---|---|---|
| Gate 1 | `AWAITING_APPROVAL -> APPROVED` | Hashes of the reviewed spec and plan |
| Gate 3 | `WORKTREE_REVIEW` / `MULTI_AGENT_CODE_REVIEW` `-> VERIFY_EXIT` | Commit SHA, tracked-diff hash, untracked-files hash |
| Closure | Every edge into `DONE` | Worktree hashes plus the retrospective digest |

Each edge declares `requires_cryptographic_proof` in `transition_templates.yaml`. The coordinator halts with `HUMAN_PROOF_REQUIRED` and a `transition_request`; the human signs it with `ssh-keygen -Y sign` (OpenSSH prompts for the passphrase); the signature is verified against `allowed_signers` and the request is consumed exactly once in the commit transaction. A request expires after 15 minutes and is bound to the content it lists: change the worktree and it must be re-issued.

---

## 2. The Iron Law

**AGENTS SHALL NEVER RUN SIGNING COMMANDS, MANIPULATE KEYS, OR SYNTHESIZE HUMAN APPROVAL PROOF.**

---

## 3. Invariants & Forbidden Actions

- Never run `setup_ciba_identity.py`, `ssh-keygen -Y sign`, `show-challenge` or `approve-transition`.
- Never create, read, or move a private key, or edit `allowed_signers*`.
- Never offer a prompt, typed word, `--answers`, `--human-confirmed`, flag, or actor string as authorization for cryptographic edges.
- Never record a decision on the human's behalf.
- Never bypass or work around a `HUMAN_PROOF_REQUIRED` refusal; report it and provide the exact command for the human to run in their own terminal.
- `os-init` and `os-health-check` only report signing readiness (read-only); they never enroll a key.

---

## 4. Evaluation Checklist

Before reporting gate status:
- Is cryptographic proof required for this target transition?
- Did the coordinator yield `HUMAN_PROOF_REQUIRED`?
- Has the human executed the signing command directly in their terminal?
