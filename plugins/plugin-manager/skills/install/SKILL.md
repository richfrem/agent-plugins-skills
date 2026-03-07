---
description: >-
  Replicate a specific plugin from this project's plugins/ folder to a target
  project, then activate it in the target's agent environments.
args:
  plugin_name:
    description: "The name of the plugin to replicate (e.g., rlm-factory)."
    type: string
    required: true
  dest:
    description: "Absolute path to the target project's plugins/ folder."
    type: string
    required: true
---

# Install Plugin to Target

Copies a plugin from this repo's `plugins/` to a target project's `plugins/` folder, then activates it in that project's agent environments.

```bash
PLUGIN_NAME="${plugin_name}"
SOURCE_PATH="$(pwd)/plugins/$PLUGIN_NAME"
TARGET_PLUGINS="${dest}"
DEST_PATH="$TARGET_PLUGINS/$PLUGIN_NAME"

# Validate source plugin exists
if [ ! -d "$SOURCE_PATH" ]; then
    echo "Error: Plugin '$PLUGIN_NAME' not found in plugins/."
    echo "Available plugins:"
    ls plugins/
    exit 1
fi

# Replicate source -> dest (additive update)
python3 plugins/plugin-manager/skills/*/scripts/plugin_replicator.py \
  --source "$SOURCE_PATH" \
  --dest "$DEST_PATH"

# Activate in target's agent environments
echo "Activating plugin in target project..."
cd "$TARGET_PLUGINS/.." && python3 plugins/plugin-manager/skills/*/scripts/sync_with_inventory.py
```

> To also remove deleted files, add `--clean` to the `plugin_replicator.py` call.
> To replicate all plugins at once, use `/plugin-manager:update` or `bulk_replicator.py`.
