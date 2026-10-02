---
name: os-control-plane-mode
plugin: agent-agentic-os
version: 1.1.0
description: >
  Enable, disable, or check the Agentic OS control plane as one unit, on demand. Use the full
  pipeline for big tasks where its overhead pays off, and switch it off for quick tasks to save
  context and time. Trigger on: "enable the control plane", "disable the control plane",
  "turn on / turn off the control plane", "turn off work-intake", "turn on work-intake",
  "stop gating my commits and pushes", "turn off the push guard", "turn off the commit guard",
  "is the control plane on", "control plane status", "which mode is the control plane in".
  Do NOT use this to run work-intake itself or to get past a blocked hook.
allowed-tools: Bash, Read
---

# Control Plane Mode (`os-control-plane-mode`)

The control plane is more than one switch: the `work-intake` family of skills, a rule, two git guards in `.git/hooks`, and a declared mode. This skill flips them together and proves the result, so a repo is never left half on.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [What Each Mode Does](#what-each-mode-does)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Explicit Request Only**: Only on explicit user request naming control plane or gating. Never autonomously.
2. **Never Bypass Blocked Guards**: A blocked guard means stop, report why, and ask.
3. **Confirm Before Applying**: Run `--dry-run`, explain plan, and require explicit confirmation before `--yes`.
4. **No Manual Hook Edits**: Do not edit `AGENTS.md`, hooks, or ownership files manually. Use the CLI script.

## Quick start

Check current control plane mode and consistency:

```bash
python3 scripts/control_plane_mode.py status
```

## Workflow

1. **Check Status**: Inspect `status` output to see active mode and hook wiring.
2. **Dry Run Plan**: Execute `disable --dry-run` or `enable --dry-run` to preview actions.
3. **Execute Toggle**: With user confirmation, apply with `--yes`:
   ```bash
   python3 scripts/control_plane_mode.py disable --yes
   ```
4. **Re-verify**: Run `status` to confirm expected state.

## What Each Mode Does

| Mode | Order | Rationale |
|---|---|---|
| `disable` | declare `disabled` -> unwire guards -> ownership -> sync | gates go off first; machinery removed after |
| `enable` | ownership -> sync -> install/wire guards -> declare `enabled` | gates only come on once machinery exists |

## Verification

Confirm consistency and exit code (`0` = consistent):

```bash
python3 scripts/control_plane_mode.py status --json
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for control plane state toggles.
- [fallback-tree.md](references/fallback-tree.md) — Recovery procedures when toggling or syncing fails.
- [control-plane.manifest.json](references/control-plane.manifest.json) — Declared manifest of control plane members and git guards.
