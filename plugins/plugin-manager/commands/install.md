---
description: >-
  Install a specific plugin into the local agent environments from either
  a GitHub source or local plugins folder. Tracks installation in plugin-sources.json.
args:
  source:
    description: "GitHub slug (e.g. richfrem/agent-plugins-skills) or local path (e.g. plugins/agent-loops). Leave blank for interactive TUI."
    type: string
    required: false
  plugin_name:
    description: "Specific plugin name to install headlessly (requires source). Leave blank for interactive TUI."
    type: string
    required: false
---

# Install Plugin

Installs one or more plugins into `.agents/` (and other agent environments), then records
the installation in `plugin-sources.json`.

```bash
if [ -n "${plugin_name}" ] && [ -n "${source}" ]; then
    # Headless: install a specific plugin from a given source
    python plugins/plugin-manager/scripts/plugin_add.py "${source}" --plugins "${plugin_name}" --yes
elif [ -n "${source}" ]; then
    # Interactive picker for a specific source
    python plugins/plugin-manager/scripts/plugin_add.py "${source}"
else
    # Interactive picker — GitHub registry
    python plugins/plugin-manager/scripts/plugin_add.py richfrem/agent-plugins-skills
fi
```

> To sync all installed plugins at once, use `/plugin-manager:sync`.
> To remove an installed plugin, use `/plugin-manager:remove`.
