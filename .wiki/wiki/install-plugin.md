---
concept: install-plugin
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/plugin-manager_install.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.323318+00:00
cluster: plugin-code
content_hash: a5346b4bcd0dfcdb
---

# Install Plugin

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
    python ././scripts/plugin_add.py "${plugin_name}" -y
else
    # Interactive picker
    python ././scripts/plugin_add.py
fi
```

> To install everything, use the `/plugin-manager:update` command.


## See Also

- [[adr-manager-plugin]]
- [[test-scenario-bank-agentic-os-plugin]]
- [[agent-plugin-analyzer]]
- [[adr-001-cross-plugin-script-dependencies]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[adr-004-self-contained-plugins---no-cross-plugin-script-dependencies]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/plugin-manager_install.md`
- **Indexed:** 2026-04-17T06:42:10.323318+00:00
