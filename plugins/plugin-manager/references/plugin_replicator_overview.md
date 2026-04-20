# Plugin Replicator Overview

The **Plugin Replicator** syncs plugin source code between local project repositories using explicit `--source` and `--dest` paths. It works in **both directions**:

## Push (from `agent-plugins-skills` outward)
Use when you want to distribute an update from this central repo to a consumer project:
```bash
python ./plugin_replicator.py \
  --source <APS_ROOT>/plugins/rlm-factory \
  --dest <USER_HOME>/Projects/Project_Sanctuary/plugins/rlm-factory
```

## Pull (from a consumer project inward)
Use when you're inside a consumer project and want to pull the latest from this central repo:
```bash
# Run from Project_Sanctuary
python ./plugin_replicator.py \
  --source <USER_HOME>/Projects/agent-plugins-skills/plugins/rlm-factory \
  --dest <PROJECT_ROOT>/plugins/rlm-factory \
  --clean
```

## Bulk Sync
```bash
python ./bulk_replicator.py \
  --source <USER_HOME>/Projects/agent-plugins-skills/plugins/ \
  --dest <PROJECT_ROOT>/plugins/
```

## Modes

| Mode | Flag | Description | Best For |
| :--- | :--- | :--- | :--- |
| **Additive** | (Default) | Copies new/updated files. Never deletes from dest. | Safe everyday updates |
| **Clean** | `--clean` | Copies new/updated AND removes files missing from source. | Full sync incl. deletions |
| **Link** | `--link` | Creates a live symlink. Always reflects source. | Active development |
| **Preview** | `--dry-run` | Prints what would happen without applying changes. | First-time verification |

## See Also
- [Flow Diagram](../assets/diagrams/plugin_replicator_diagram.mmd)
- `bulk_replicator.py` - for syncing the entire plugin suite at once
- `maintain-plugins` skill - activate replicated plugins in agent environments
