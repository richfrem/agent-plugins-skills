---
name: os-memory-manager
plugin: agent-agentic-os
description: >
  Trigger with "remember this", "update memory", "what should we record from this session",
  "capture learnings", "write a session log", or when closing a session. Guides agents on
  managing memory hygiene across sessions, deciding what to write to dated memory logs, what
  to promote to long-term memory.md, and when to archive.
allowed-tools: Bash, Read, Write
---

# Session Memory Manager (`os-memory-manager`)

Manages the three tiers of agent memory in an Agentic OS environment: Auto-memory (`MEMORY.md`), Long-term facts (`context/memory.md`), and Session logs (`context/memory/YYYY-MM-DD.md`).

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Conflict Resolution**: Never overwrite `context/memory.md` with conflicting facts without prompt and resolution.
2. **Enduring Facts Only**: Do not promote ephemeral error messages, test noise, or single-use bash commands.
3. **Lock Release**: Always release `memory` lock upon completion or error recovery.

## Quick start

Check current memory file size and status:

```bash
wc -c context/memory.md
```

## Workflow

1. **Acquire Lock**: Acquire `memory` lock via `kernel.py`:
   ```bash
   python3 scripts/kernel.py acquire_lock memory
   ```
2. **Record Session Log**: Write dated session summary to `context/memory/YYYY-MM-DD.md`.
3. **Promote Long-Term Facts**: Append vetted architectural decisions to `context/memory.md` with conflict checks.
4. **Enforce Size Limits**: If `context/memory.md` exceeds 50,000 bytes, prune or archive oldest entries to `context/memory/archive/`.
5. **Release Lock**:
   ```bash
   python3 scripts/kernel.py release_lock memory
   ```

## Verification

Confirm memory update is persisted and lock is released:

```bash
python3 scripts/kernel.py state_read
```

## References

- [detailed-reference.md](references/detailed-reference.md) — Tiered memory architectures and promotion protocols.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for memory promotions.
- [fallback-tree.md](references/fallback-tree.md) — Recovery procedures when locks fail or collisions occur.
