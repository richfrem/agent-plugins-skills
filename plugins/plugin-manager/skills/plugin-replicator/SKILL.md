---
name: plugin-replicator
description: >
  Replicates plugin source code from one project's plugins/ directory to another
  project's plugins/ directory on the same machine. Supports additive-update (default),
  clean-sync (--clean), symlink (--link), and dry-run modes. Trigger when setting up a
  new project workspace, distributing plugins to consumer projects, or syncing plugin
  updates across local repos.
allowed-tools: Bash, Write, Read
---

# Plugin Replicator

## Overview
This skill copies plugin source code FROM this central repo TO another project's `plugins/` folder. It does **not** deploy to agent environments (`.agent/`, `.claude/` etc.) — that is handled by `plugin-maintenance` Sync in the target project.

**The pipeline:**
```
plugin-replicator          → copies plugin/ code  → /other-project/plugins/
plugin-maintenance sync    → installs into         → /other-project/.agent/, .gemini/, etc.
```

## References
- Overview: `plugins/plugin-manager/skills/plugin-replicator/references/plugin_replicator_overview.md`
- Flow diagram: `plugins/plugin-manager/skills/plugin-replicator/references/plugin_replicator_diagram.mmd`

---

## Modes

| Mode | Flag | Behavior |
|------|------|----------|
| **Additive** | (default) | Copies new/updated files only. Nothing deleted from dest. |
| **Clean Sync** | `--clean` | Copies new/updated AND removes dest files missing from source. |
| **Symlink** | `--link` | Creates a live symlink — always reflects source. Best for dev. |
| **Preview** | `--dry-run` | Prints what would happen without making changes. |

---

## Execution Protocol

> **CRITICAL**: Do not immediately generate bash commands. Operate as an interactive assistant.

### Phase 1: Guided Discovery

Ask the user:
1. **Source**: Which plugin(s)? Single plugin or bulk sync of all?
2. **Destination**: What is the absolute path to the target project's `plugins/` folder?
3. **Mode**: Additive update (safe default), Clean sync (also removes deleted files), or Symlink (dev)?
4. **Preview first?**: Recommend `--dry-run` for the first run.

### Phase 2: Recap-Before-Execute

```markdown
### Proposed Replication Task
- **Plugin(s)**: [name or ALL]
- **Source**: `plugins/<name>/` (this repo)
- **Destination**: `[absolute path]`
- **Mode**: [Additive / Clean / Symlink] [DRY RUN?]

> Confirm to proceed.
```

### Phase 3: Command Generation

#### Single Plugin — Additive Update (default)
```bash
python3 plugins/plugin-manager/scripts/plugin_replicator.py \
  --source plugins/<plugin-name> \
  --dest /path/to/other-project/plugins/<plugin-name>
```

#### Single Plugin — Clean Sync (also removes deleted files)
```bash
python3 plugins/plugin-manager/scripts/plugin_replicator.py \
  --source plugins/<plugin-name> \
  --dest /path/to/other-project/plugins/<plugin-name> \
  --clean
```

#### Single Plugin — Preview First
```bash
python3 plugins/plugin-manager/scripts/plugin_replicator.py \
  --source plugins/<plugin-name> \
  --dest /path/to/other-project/plugins/<plugin-name> \
  --dry-run
```

#### All Plugins — Bulk Sync
```bash
python3 plugins/plugin-manager/scripts/bulk_replicator.py \
  --source plugins/ \
  --dest /path/to/other-project/plugins/
```

#### Filtered Bulk (e.g., only obsidian-* plugins)
```bash
python3 plugins/plugin-manager/scripts/bulk_replicator.py \
  --source plugins/ \
  --dest /path/to/other-project/plugins/ \
  --filter "obsidian-*" --clean
```

---

## When to Use
- **New project setup**: Bulk-replicate all plugins to get started fast.
- **Plugin update**: Additive sync to push latest changes to a consumer project.
- **Removing a skill/file**: Run with `--clean` to propagate deletions.
- **Active development**: Use `--link` to work from source and test in target instantly.

## Next Actions
After replicating, run `plugin-maintenance` Sync in the target project to activate the plugins in `.agent/`, `.claude/`, `.gemini/` etc.
