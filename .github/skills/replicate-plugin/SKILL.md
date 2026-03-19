---
name: replicate-plugin
description: >-
  Developer machine tool for replicating plugin source code between local project
  repositories. Use when you want to push plugin updates from agent-plugins-skills
  to a consumer project, or pull the latest plugins into a consumer project from
  this central repo. Works with explicit --source and --dest paths; supports
  additive-update (default), --clean (also removes deleted files), --link (symlink),
  and --dry-run modes.
allowed-tools: Bash, Write, Read
---
# Plugin Replicator

## Overview
**Primarily a developer machine tool.** Use this when you have multiple local projects and want to keep plugin source code in sync between them without manual copying.

It is **bidirectional** — source and destination are just paths, so it works as both a push (distribute updates outward) and pull (pull latest into a consumer project):

```
PUSH (run from agent-plugins-skills):
  plugins/X  ->  /other-project/plugins/X

PULL (run from the consumer project):
  /agent-plugins-skills/plugins/X  ->  plugins/X
```

After replicating, run `maintain-plugins` Sync in the target project to activate plugins in `.agent/`, `.claude/`, `.gemini/` etc.


## References
- Overview: `../../references/plugin_replicator_overview.md`
- Flow diagram: `../../references/plugin_replicator_diagram.mmd`

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

#### Pull: From `agent-plugins-skills` into a consumer project (run FROM consumer project)
```bash
python3 ./scripts/plugin_replicator.py \
  --source /Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/<plugin-name> \
  --dest plugins/<plugin-name> \
  --clean
```

#### Push: From this repo to another project (run FROM this repo)
```bash
python3 ./scripts/plugin_replicator.py \
  --source plugins/<plugin-name> \
  --dest /path/to/other-project/plugins/<plugin-name>
```

#### Bulk Push: All plugins
```bash
python3 ./scripts/bulk_replicator.py \
  --source plugins/ \
  --dest /path/to/other-project/plugins/
```

#### Filtered Bulk (e.g., only obsidian-* plugins)
```bash
python3 ./scripts/bulk_replicator.py \
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
After replicating, run `maintain-plugins` Sync in the target project to activate the plugins in `.agent/`, `.claude/`, `.gemini/` etc.
