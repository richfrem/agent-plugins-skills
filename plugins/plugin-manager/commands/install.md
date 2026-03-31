---
description: >-
  Install a specific plugin natively into the local agent environments from either
  the remote registry or local plugins folder.
args:
  plugin_name:
    description: "The name of the plugin to install (e.g., rlm-factory). Leave blank for interactive TUI."
    type: string
    required: false
---

# Install Plugin

Installs a plugin into the local `.agents/` directory (and other agent environments).

```bash
if [ -n "${plugin_name}" ]; then
    # Headless install
    python ./plugins/plugin-manager/scripts/plugin_add.py "${plugin_name}" -y
else
    # Interactive picker
    python ./plugins/plugin-manager/scripts/plugin_add.py
fi
```

> To install everything, use the `/plugin-manager:update` command.
