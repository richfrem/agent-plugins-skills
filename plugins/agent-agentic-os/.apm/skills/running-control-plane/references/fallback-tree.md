# Fallback Tree: running-control-plane

Merged verbatim from the retired skills; one section per mode. Headings inside a section are one level deeper than in the original.

## Contents

- [Mode: intake](#mode-intake)
- [Mode: mode](#mode-mode)
- [Mode: health](#mode-health)
- [Mode: simulator](#mode-simulator)

## Mode: intake

1. Claude Code Native -> 2. Antigravity IDE Artifact -> 3. Socratic Fallback CLI

## Mode: mode

Start from the symptom. Every command here is safe to repeat.

| Symptom | Meaning | Do this |
|---|---|---|
| `status` exit 1, "not wired" / "script missing" while enabled | Hooks were reset or reinstalled by something else | Run `enable --yes`; it reinstalls and rewires the guards |
| `status` warns "still wired (inert)" while disabled | A guard is wired but exits 0 because of the mode | Harmless; `disable --yes` unwires it |
| `status` warns "stale" | The guard in `.git/hooks` was stamped for another install location, or differs from the installed skill's copy (typical after `apm update` or a move) | Run `enable --yes`; it reinstalls the guard and re-stamps the current script paths |
| Exit 2: "cannot enable: guard script source not found" | The installed skill is incomplete (a guard script is missing beside `control_plane_mode.py`) | Reinstall the skill (`apm install`), then retry |
| "unrecognized" for a dispatcher hook | A hand-edited hook mentions the guard in a different shape | Left untouched on purpose. The guard still exits 0 while disabled. Edit the hook by hand if you want it unwired |
| "mode file must contain 'enabled' or 'disabled'" | `context/control-plane-mode` is corrupt | Delete the file (missing means enabled) or write a valid word, then run `status` |
| Gates still blocking after `disable` | You are in a different clone, or hooks were reinstalled afterwards | Run `status` in that clone; the mode and the hooks are per clone (worktrees share the main checkout's) |
| `status` warns `.git/hooks` is missing | Not a git checkout, or a bare clone | Nothing to wire; the mode file is still written |

### Undo

Each toggle backs up the mode file and the dispatcher hooks to `context/control-plane-backup/<timestamp>/`. Re-running the opposite toggle is the normal undo; the backup is the manual one.

## Mode: health

1. Deterministic scan of events.jsonl/os-state.json/memory.md via kernel.py -> 2. If kernel.py unavailable, fall back to direct file existence + line-count checks.

## Mode: simulator

1. If the requested transition is unknown, stop and report the valid transition names.
2. If deterministic simulation fails, inspect the raw reply and identify whether the
   guidance template or coordinator logic is at fault.
3. If the behavioral simulation fails, fix the specific guidance or question-handling
   defect and retry the same edge.
4. After three failed attempts, stop and escalate with all attempt evidence.
5. Never replace a failed behavioral test with a structural-only pass.
