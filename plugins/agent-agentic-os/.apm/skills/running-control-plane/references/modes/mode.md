# Control Plane Mode

Switch commit and push gating on or off for this clone, and prove the result. The skill stays installed either way: APM owns installation, this workflow owns only the per-clone switch.

## When to use

Carried over from the description of the former skill, so its trigger phrases and exclusions stay on record:

> Enable, disable, or check the Agentic OS control plane as one unit, on demand. Use the full pipeline for big tasks where its overhead pays off, and switch it off for quick tasks to save context and time. Trigger on: "enable the control plane", "disable the control plane", "turn on / turn off the control plane", "turn off the `intake` mode", "turn on the `intake` mode", "stop gating my commits and pushes", "turn off the push guard", "turn off the commit guard", "is the control plane on", "control plane status", "which mode is the control plane in". Do NOT use this to run the `intake` mode itself or to get past a blocked hook.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [What Each Mode Does](#what-each-mode-does)
- [What changed from the former `os-control-mode` skill](#what-changed-from-the-former-os-control-mode-skill)
- [Where the switch lives](#where-the-switch-lives)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Explicit Request Only**: Only on explicit user request naming the control plane or gating. Never autonomously.
2. **Never Bypass Blocked Guards**: A blocked guard means stop, report why, and ask.
3. **Confirm Before Applying**: Run `--dry-run`, explain the plan, and require explicit confirmation before `--yes`.
4. **No Manual Hook Edits**: Do not edit `AGENTS.md` or `.git/hooks` by hand. Use the script.
5. **Intake follows the mode**: when the mode is `disabled`, the intake mode reports it and skips registration and gating.

## Quick start

Check the current mode and consistency:

```bash
python3 scripts/control_plane_mode.py status
```

## Workflow

1. **Check Status**: Inspect `status` for the declared mode and the guard wiring.
2. **Dry Run Plan**: Run `disable --dry-run` or `enable --dry-run` to preview.
3. **Execute Toggle**: With the user's confirmation, apply it:
   ```bash
   python3 scripts/control_plane_mode.py disable --yes --actor <name>
   ```
4. **Re-verify**: Run `status` and confirm `RESULT: consistent`.

## What Each Mode Does

| Mode | Order | Rationale |
|---|---|---|
| `disable` | declare `disabled` -> unwire the guards | gates go off first; the guard scripts stay for a fast re-enable |
| `enable` | install and wire the guards -> declare `enabled` | gates only come on once the machinery exists |

Never touched: `context/control_plane.db` and its task history, the Claude Code plugin hooks, and the evolution guard (a separate feature with its own gate).

## What changed from the former `os-control-mode` skill

The toggle was rewritten when the 14 skills became 3 (the syncer it called had already been retired). This is the complete list of what it no longer does, and why.

| Former behavior | Now | Why |
|---|---|---|
| Switched the **skills** `os-control-intake`, `os-control-simulator`, `os-control-signing-setup` on and off | Dropped. Skills stay installed; only gating changes | Those are now modes of one skill; APM, not this script, owns installation |
| Switched the `state-transition-guidance-compliance` **rule** on and off | Dropped | Plugin rules are not installed by APM and are copied by init; a follow-up if wanted |
| Edited the **ownership file** (`.agents/ownership/agent-agentic-os.json`) | Dropped | The file belonged to the retired plugin-manager |
| Ran the **plugin-syncer** after the change; `--no-sync` and `--syncer` flags; exit code 3 for a failed sync | Dropped | The syncer was retired with plugin-manager (PR #712) |
| Read `control-plane.manifest.json` (members, excluded, never_removed) and a test that every component naming the control plane was classified | Dropped | The manifest only listed skills and rules to toggle; the guards and the mode file are defined in `control_plane_hooks.py` |
| Warned that disabling deleted git-tracked member files, and flagged uncommitted deletions | Dropped | Nothing is removed from the working tree any more |

Kept: the declared mode in `context/control-plane-mode`, installing and wiring (or unwiring) the commit and push guards, `--dry-run` and `--yes`, the actor log, the backup under `context/control-plane-backup/`, `status` with `--json`, the stale-guard check, and the guards themselves exiting 0 when the mode is `disabled`.

Added: the guards are stamped with the installed skill's script paths, and a test runs the script from a copy deployed like an APM install.

## Where the switch lives

- The declared mode is `context/control-plane-mode` (one word: `enabled` or `disabled`; a missing file means `enabled`). It is per clone and not committed. Every worktree of a clone reads the main checkout's file.
- The two guards, `pre-commit-pipeline-guard` and `pre-push-review-guard`, are copied into `.git/hooks`, and they read the same file and exit 0 when it says `disabled`. They are stamped at install time with the real location of this skill's scripts, so they work for project and global APM installs.
- After `apm update`, the copies in `.git/hooks` keep the old stamp. `status` reports them as stale; run `enable --yes` to refresh them.
- Backups of the mode file and hook dispatchers go to `context/control-plane-backup/<timestamp>/` before any change.

## Verification

Confirm consistency and exit code (`0` = consistent):

```bash
python3 scripts/control_plane_mode.py status --json
```

## References

- [acceptance-criteria.md](../acceptance-criteria.md#mode-mode) — Acceptance criteria for control plane state toggles.
- [fallback-tree.md](../fallback-tree.md#mode-mode) — Recovery procedures when toggling fails.
