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

The control plane is more than one switch: the `work-intake` family of skills, a rule, two git
guards in `.git/hooks`, and a declared mode. This skill flips them together and proves the result,
so a repo is never left half on. It exists so the pipeline can be used for larger work and turned
off for simple tasks, where it only costs context and speed.

## Critical Operational Rules (read first)

1. **Only on the user's explicit request** naming the control plane, `work-intake` gating, or the
   commit/push guards. Never on your own initiative.
2. **Never use it to get past a blocked commit or push.** A guard that blocks means: stop, report
   why, and ask. If the user wants the gates off, that is a deliberate `disable`, not a workaround.
3. **Always show the plan and get a clear "yes" before applying.** Run `--dry-run`, show the plan in
   plain words, and pass `--yes` only after the user confirms. Disabling removes installed files.
4. **Run `status` afterwards and report its output.** Do not say "done" without it.
5. **Do not edit `AGENTS.md`, hooks or the ownership file by hand to achieve this.** The script
   backs up what it changes and keeps the pieces consistent.

## Commands

Run from the repository root. In an installed repo the script is at
`.agents/skills/os-control-plane-mode/scripts/control_plane_mode.py`.

```bash
python3 .agents/skills/os-control-plane-mode/scripts/control_plane_mode.py status            # read-only
python3 .agents/skills/os-control-plane-mode/scripts/control_plane_mode.py disable --dry-run
python3 .agents/skills/os-control-plane-mode/scripts/control_plane_mode.py disable --yes
python3 .agents/skills/os-control-plane-mode/scripts/control_plane_mode.py enable --dry-run
python3 .agents/skills/os-control-plane-mode/scripts/control_plane_mode.py enable --yes
```

`status --json` is machine-readable. Exit codes: `0` consistent, `1` inconsistent, `2` refused or
bad input, `3` the plugin sync failed.

## What each mode does

| | `disable` | `enable` |
|---|---|---|
| Order | declare `disabled` -> unwire guards -> ownership -> sync | ownership -> sync -> install + wire guards -> declare `enabled` |
| Why this order | gates go off first and the machinery is removed after | gates only come on once the machinery exists |

The members, guards and exclusions are declared in `control-plane.manifest.json` in this skill, and
a test fails if any component mentions the control plane without being classified there.

**Disable** declares `disabled`, unwires `pre-commit-pipeline-guard` and `pre-push-review-guard`
from `.git/hooks` (their scripts are kept, and they also exit 0 on their own while disabled), sets
`should_install: false` for the member skills and rule, and runs the plugin syncer so they are
removed. **Enable** does the reverse and refreshes the guard scripts from the plugin.

**Never touched by either:** `context/control_plane.db` and its task history; `os-init` and
`os-health-check`; the Claude Code plugin hooks (memory, metrics, evolution turn guard); and the
independent `pre-commit-evolution-guard` and its CI gate (map-debt / evolution-log discipline).
Tell the user that last one keeps applying, because it surprises people.

## After a toggle

- Report the `status` output: mode, which members are installed, which guards are wired.
- If `status` warns that `AGENTS.md` still says Phase 0 intake is mandatory, tell the user; the
  wording belongs to them. It should be conditional on the control plane being enabled.
- Skills removed or added are picked up by the next session. In the current session, stop or start
  using `work-intake` according to the new mode.
- A toggle affects every worktree of the repository (hooks and the database are shared).
- **Tracked member files show as deleted.** If the repo tracks any member file in git (for example
  `.agent/rules/`), `disable` removes it from the working tree, so git shows it as deleted. The plan
  warns about this beforehand and `status` flags it as an "uncommitted deletion". Tell the user and
  **do not commit those deletions**; `enable` restores the identical file. (`.agents/` is normally
  gitignored, so skills do not have this effect.)
- **The sync takes a minute or more** (it refreshes every registered plugin). Run the command with a
  long timeout and do not interrupt it; if it fails the command is safe to repeat.
- **The syncer rewrites the ownership file and bumps its `installed_at` line** on every run, so expect
  that one line to differ after any toggle. The `should_install` flags are what the toggle controls.
- **`status` manages only the manifest members.** Other components that happen to be off (for example
  `self-evolution`) are not part of the toggle and are not changed or reported as problems.

## When something is off

See `references/fallback-tree.md`. In short: `status` exit 1 means drift (re-run the toggle to
reconcile); exit 3 means the sync failed after earlier steps succeeded (fix it and re-run the same
command, which is safe to repeat); a hook shape the tool does not recognise is reported and left
untouched, never guessed at.

## Related

- `os-init` installs the control plane and honours this mode: re-running it with the mode
  `disabled` does not re-wire the guards.
- `os-health-check` reports `disabled` as an intentional state, and flags a mode that does not
  match the repo.
- `work-intake` is the pipeline entry point this skill switches on and off.
