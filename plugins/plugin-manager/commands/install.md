---
description: >
  Install a specific plugin from the vendor collection into this project,
  then sync it to all agent environments.
args:
  plugin_name:
    description: "The name of the plugin to install (e.g., rlm-factory)."
    type: string
    required: true
---

# Install Plugin

Installs a plugin from `.vendor/agent-plugins-skills/plugins/` into the local `plugins/` directory and activates it in all agent environments.

```bash
PLUGIN_NAME="${plugin_name}"
VENDOR_PATH=".vendor/agent-plugins-skills/plugins/$PLUGIN_NAME"
TARGET_PATH="plugins/$PLUGIN_NAME"

# Validate plugin exists in vendor
if [ ! -d "$VENDOR_PATH" ]; then
    echo "Error: Plugin '$PLUGIN_NAME' not found in vendor collection."
    echo "Available plugins:"
    ls .vendor/agent-plugins-skills/plugins/
    exit 1
fi

# Copy from vendor to local
if [ -d "$TARGET_PATH" ]; then
    echo "Plugin '$PLUGIN_NAME' already installed — updating..."
else
    echo "Installing '$PLUGIN_NAME'..."
fi
cp -r "$VENDOR_PATH" "plugins/"

# Activate in all agent environments
echo "Activating plugin capabilities..."
python3 plugins/plugin-mapper/skills/agent-bridge/scripts/install_all_plugins.py
```

> To install from a different source or link instead of copy, use the `plugin-replicator` skill.
