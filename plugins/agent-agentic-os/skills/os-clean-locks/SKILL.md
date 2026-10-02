---
name: os-clean-locks
plugin: agent-agentic-os
description: >
  Safely removes all agent lock files from the context/.locks/ directory to resolve
  deadlocks caused by crashed agents leaving stale locks behind. Use when the user says
  "/os-clean-locks", "clear all locks", "reset agent locks", or when an agent is deadlocked
  and cannot acquire a lock because a previous agent crashed and left a stale lock behind
  in context/.locks/. Verifies lock existence, discovers and removes stale lock directories,
  updates OS state via kernel.py, and emits event bus notifications. Requires Python 3.8+
  standard library only.
allowed-tools: Bash, Read, Write
---

# OS Clean Locks (`os-clean-locks`)

Safely remove agent lock directories from `context/.locks/` to resolve deadlocks caused by crashed agents leaving stale locks behind.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Target Only Lock Directories**: Never delete files outside `context/.locks/`.
2. **Atomic Recovery**: Verify lock directory existence before executing removal.
3. **State Synchronization**: Update OS state and emit result event via `kernel.py` when available.

## Quick start

Check for active or stale locks in the lock directory:

```bash
ls -la context/.locks/
```

## Workflow

1. **Emit Intent**: If `kernel.py` exists, notify the Event Bus:
   ```bash
   python3 scripts/kernel.py emit_event --agent os-clean-locks --type intent --action clear_locks
   ```
2. **Discover Locks**: Inspect `context/.locks/` for directory entries ending in `.lock`.
3. **Safely Remove**: Delete each stale `.lock` directory:
   ```bash
   rm -rf context/.locks/*.lock
   ```
4. **Update OS State & Notify**:
   ```bash
   python3 scripts/kernel.py state_update locks_cleared true
   python3 scripts/kernel.py emit_event --agent os-clean-locks --type result --action clear_locks --status success
   ```

## Verification

Confirm `context/.locks/` contains no stale lock directories:

```bash
ls -la context/.locks/
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for lock clearance operations.
- [fallback-tree.md](references/fallback-tree.md) — Remediation pathways if locks cannot be removed.
