# Session Bootstrap

<!-- Run this at the start of each session to load context -->

## First Time in This Clone? Set Up the Substrate Once

Skip this section on every session after the first. If `context/control_plane.db` doesn't exist
yet, run these once (assumes plugins are already installed per
[INSTALL.md's "Local Development (For Developers)"](INSTALL.md#local-development-for-developers)
— `git clone` + `plugin_add.py --all -y`):

```bash
python3 plugins/agent-agentic-os/scripts/init_agentic_os.py --target .
```

This wires `.git/hooks/pre-commit-evolution-guard` and `.git/hooks/pre-push-review-guard`,
initializes `context/control_plane.db` (self-healing schema, see [`docs/ADRs/`](docs/ADRs/)),
and scaffolds `context/memory/`, `context/status.md`, and `.claude/hooks/hooks.json`.
Re-running against an existing local setup instead uses `--retrofit` — see
[`os-control-init/SKILL.md`](plugins/agent-agentic-os/skills/os-control-init/SKILL.md). It creates `.bak` files
when updating existing guideline files (`CLAUDE.md`, `GEMINI.md`, `AGENTS.md`) — **do not blindly
delete them**; review `git diff` and reconcile local customizations first.

Then confirm the substrate is active:

```bash
test -f context/control_plane.db && echo "OK control_plane.db" || echo "MISSING control_plane.db"
test -f .claude/hooks/hooks.json && echo "OK hooks.json" || echo "MISSING hooks.json"
```

Or invoke **`/os-control-health`** for the full audit (Event Bus, locks, memory arrays, substrate
completeness). Then verify the test suite: `python3 -m pytest plugins/ -q`. See
[`CLAUDE.md`](CLAUDE.md) for the full development workflow once the substrate is confirmed.

## Load Context

1. @import context/soul.md (agent identity)
2. @import context/user.md (user preferences)
3. @import context/memory.md (last 20 facts)
4. Check context/memory/ for recent session logs (last 7 days)

## Check Open Items

Look for `[ ]` items in context/memory/ session logs from the last 7 days.

## Next Session Priorities (APM Migration)

- **Target Plan**: [`docs/plans/apm_migration_plan.md`](docs/plans/apm_migration_plan.md)
- **Goal**: Transition from `uvx` / `plugin-manager` orchestration to Microsoft APM (Agent Package Manager) using a Strangler Fig approach.
- **Immediate Task**: Execute Phase 1 Pilot Proof-of-Concept:
  1. Build dereferencer pipeline (`inspect → normalize → validate → package → test deploy`) under `plugins/agent-scaffolders/skills/convert-plugin-to-apm/`.
  2. Synthesize pilot `apm.yml` for `agent-scaffolders` with target mappings (`copilot`, `claude`, `agents`).
  3. Validate against the Acceptance Verification Contract in `docs/plans/apm_migration_plan.md`.

## Confirm Readiness

Say: "I am ready. Here is what I know: [brief summary of loaded context and open items]"
