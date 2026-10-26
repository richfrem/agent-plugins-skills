# Session Bootstrap

<!-- Read at the start of each session: orientation only. Task steps live in the linked plans and skills. -->

## Rules First

[`AGENTS.md`](AGENTS.md) is the single source of agent instructions. Read it before acting, and
re-read its git/worktree rules before any commit or branch step.

## First Time in This Clone?

If `context/control_plane.db` does not exist yet, set up the substrate once:

- Install per [INSTALL.md — Local Development](INSTALL.md#local-development-contributors--testing).
- Initialize with `python3 plugins/agent-agentic-os/.apm/skills/setting-up-agentic-os/scripts/init_agentic_os.py --target .`
  (use `--retrofit` on an existing setup; review any `.bak` files before deleting them).
- Confirm with the checklist in `setup-healthcheck-validation.md` (in the `setting-up-agentic-os` skill), then the `health` mode of `running-control-plane`.

## Load Context

1. @import context/soul.md (agent identity)
2. @import context/user.md (user preferences)
3. @import context/memory.md (last 20 facts)
4. Check context/memory/ for recent session logs (last 7 days)

## Check Open Items

Look for `[ ]` items in context/memory/ session logs from the last 7 days, and read
[`context/status.md`](context/status.md).

## Current Focus

The repository is consolidating plugins into fewer self-contained skills: no symlinks, no
copy-manifest duplicates, APM as the only install path. The plan is the source of truth:
[`docs/plans/apm_migration_plan.md`](docs/plans/apm_migration_plan.md).

- **Where we are and what comes next**: §13.10.7 (plugin sequence and the next plugin).
- **How each plugin is migrated**: §13.5 (7-step lifecycle), §13.9.1 (pilot lessons),
  §13.10 (per-plugin subplan), §13.10.8 (inventory ledger and audit gate).
- **Downstream consuming repositories**: §12.

Do not start a plugin migration without its Step 0 baseline and inventory CSV
(`docs/plans/<plugin>_migration_inventory.csv`). Deleting skills, staging, committing and
running `apm install` need explicit user approval.

## Confirm Readiness

Say: "I am ready. Here is what I know: [brief summary of loaded context and open items]"
