# Plugin Replicator Overview

The **Plugin Replicator** is the engine that powers your "Monorepo of Plugins" workflow. It allows you to develop tools in one central location (`central-repo`) and distribute them to any number of active projects without copy-pasting code manually.

## Why use this?
*   **Single Source of Truth**: Fix a bug in `guardian-onboarding` once, sync it everywhere.
*   **Clean Projects**: Your project repos only contain the plugins they actually need.
*   **Developer Experience**: Use `--link` mode to code in the central repo and test in the target project instantly.

## Workflow

1.  **Develop**: Create/Edit a plugin in `my-plugins/plugins/new-tool`.
2.  **Replicate**: Run the replicator script targeting your active project.
    *   `python3 plugins/plugin-manager/scripts/plugin_replicator.py --plugin new-tool --target ../my-project`
3.  **Use**: The plugin is now available in `../my-project/.agent/plugins/new-tool`.

## Modes

| Mode | Flag | Description | Best For |
| :--- | :--- | :--- | :--- |
| **Copy** | (Default) | Copies all files. Is isolated from source changes until re-synced. | Production, Stable Deployments |
| **Link** | `--link` | Creates a Symlink/Junction. Changes in source reflect instantly. | Active Development |

## See Also
*   [Process Diagram](plugin_replicator_diagram.mmd)
*   [Bulk Replicator](../scripts/bulk_replicator.py) - for syncing entire suites.
