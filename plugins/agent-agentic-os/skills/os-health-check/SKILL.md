---
name: os-health-check
plugin: agent-agentic-os
description: >
  Trigger with "run health check", "check os metrics", "system monitor", or when the user
  wants to review the Agentic OS liveness metrics across the Event Bus, locks, and memory
  arrays. Scans context/events.jsonl, os-state.json, and context/memory.md deterministically
  via kernel.py — no conversational judgment required. Migrated from the former
  os-health-check agent (2026-09-05): deterministic Bash+Read diagnostic, no interview,
  no adversarial judgment — fits the skill archetype, not the agent archetype.
allowed-tools: Bash, Read
---

# OS Health Check (`os-health-check`)

Scan across `context/events.jsonl` Event Bus stream, review `os-state.json` liveness, and compile system metrics deterministically without mutating user files.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Cryptographic Verification Readiness](#cryptographic-verification-readiness)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Deterministic Diagnostic**: Do not modify user code or repo configs during health checks.
2. **Never Enroll CIBA Keys**: Check verification readiness via `--check`; never execute key enrollment scripts autonomously.
3. **Lock Hygiene**: Always release acquired monitor locks upon completion or error recovery.

## Quick start

Run a fast read-only check of the Agentic OS substrate and cryptographic readiness:

```bash
python3 scripts/setup_ciba_identity.py --check
```

## Cryptographic Verification Readiness

Assert human cryptographic gates can verify via `ssh-keygen`, SSHSIG, and `allowed_signers`:

```bash
python3 scripts/setup_ciba_identity.py --check
```

Exit 0 indicates trust anchors are ready, but is not proof of human presence. An agent must never run `setup_ciba_identity.py` to enroll keys.

## Workflow

1. **Emit Intent & Lock**: Emit intent event and acquire `monitor` lock via `kernel.py`:
   ```bash
   python3 scripts/kernel.py emit_event --agent os-health-check --type intent --action scan_metrics
   python3 scripts/kernel.py acquire_lock monitor
   ```
2. **Analyze Event Bus & State**: Inspect `context/events.jsonl`, check hook error logs, and inspect `os-state.json`.
3. **Inspect Memory & Substrate**: Review `context/memory.md` length, check `context/.locks/` for stale locks, and verify substrate components.
4. **Summarize & Release**:
   ```bash
   python3 scripts/kernel.py emit_event --agent os-health-check --type result --action scan_metrics --status success --summary "Metrics compiled"
   python3 scripts/kernel.py release_lock monitor
   ```

## Verification

Confirm monitor lock is released and event bus records clean result:

```bash
python3 scripts/kernel.py state_read
```

## References

- [detailed-reference.md](references/detailed-reference.md) — Phase specifications and deep metric inspection patterns.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Health assessment thresholds and pass/fail criteria.
- [fallback-tree.md](references/fallback-tree.md) — Remediation pathways for failed checks and leaked locks.
