# Plugin Replicator Overview

The **Plugin Replicator** allows you to develop plugins in one central location (`agent-plugins-skills`) and distribute them to any number of consumer project repos without manually copying code.

## Why use this?
- **Single Source of Truth**: Fix a bug in `rlm-factory` once, sync it everywhere.
- **Clean Projects**: Consumer repos only contain the plugins they actually need.
- **Developer Experience**: Use `--link` mode to code in the central repo and test in the target project instantly.

## Workflow

1. **Develop**: Create or edit a plugin in `plugins/my-new-tool/`.
2. **Replicate**: Run the replicator targeting your consumer project:
   ```bash
   python3 plugins/plugin-manager/scripts/plugin_replicator.py --plugin my-new-tool --target ../my-project
   ```
3. **Activate**: The plugin source is now at `../my-project/plugins/my-new-tool/`.
   Then run `plugin-maintenance sync` in the consumer project to install it into `.agent/`, `.claude/` etc.

## Modes

| Mode | Flag | Description | Best For |
| :--- | :--- | :--- | :--- |
| **Copy** | (Default) | Copies all files. Isolated from source changes until re-synced. | Production, stable deployments |
| **Link** | `--link` | Creates a symlink. Changes in source reflect instantly. | Active development |

## See Also
- [Flow Diagram](plugin_replicator_diagram.mmd)
- `plugins/plugin-manager/scripts/bulk_replicator.py` - sync entire plugin suites
- `plugin-maintenance` skill - activate replicated plugins in agent environments
