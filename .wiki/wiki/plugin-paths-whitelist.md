---
concept: plugin-paths-whitelist
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/fix-plugin-paths/scripts/plugin_paths_whitelist.json
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.239617+00:00
cluster: plugins
content_hash: 6ba7858a344c5283
---

# Plugin Paths Whitelist

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/fix-plugin-paths/scripts/plugin_paths_whitelist.json -->
{
  "global_patterns": [
    "github\\.com/.*?/plugins/",
    "<APS_ROOT>/plugins/",
    "plugins/my-",
    "plugins/<",
    "# evaluate.py lives at plugins/",
    "plugins/adr-manager",
    "plugins/link-checker",
    "e\\.g\\. `?plugins/",
    "\\(e\\.g\\., `?plugins/",
    "claude-knowledgework-plugins/",
    "plugins/agent-agentic-os/skills/os-eval-runner/",
    "Users/robert/",
    "Users/jesse/",
    "Users/username/",
    "/Users/\\..*\\.",
    "e\\.g\\.,? /Users/",
    "RESOLVES TO: plugins/",
    "PLUGIN ROOT: plugins/",
    "FILE: plugins/",
    "plugins/plugin-installer",
    "plugins/MCP",
    "plugins/[A-Z]",
    "plugins/submit",
    "plugins/scripts/",
    "plugins/plugin-name",
    "plugins/formatter",
    "plugins/agent-plugin-analyzer",
    "plugins/agent-agentic-os",
    "plugins/copilot-cli",
    "plugins/spec-kitty-plugin",
    "plugins/exploration-cycle-plugin",
    "plugins/agent-scaffolders",
    "plugins/agent-execution-disciplines",
    "plugins/[a-z-]+-plugin",
    "plugins/plugin-manager",
    "plugins/obsidian-integration",
    "plugins/rlm-factory",
    "<USER_HOME>/Projects/",
    "plugins/skills",
    "anthropics/knowledge-work-plugins/",
    "plugins/tool-inventory",
    "plugins/tool_inventory.json",
    "plugins/tools_manifest.json",
    "plugins/markdown",
    "plugins/investment-screener",
    "plugins/rsvp-speed-reader",
    "richfrem/agent-plugins-skills",
    "plugins/vector-db",
    "plugins/example_script.py",
    "plugins/task-manager",
    "@agent-plugins/",
    "plugins/ directory",
    "project's plugins/",
    "folder from plugins/",
    "maintain-plugins/"
  ],
  "file_specific_patterns": {
    "plugins/agent-agentic-os/assets/architecture-overview.md": [
      "  plugins/agent-agentic-os/          <- plugin source"
    ],
    "plugins/plugin-manager/references/plugin_replicator_overview.md": [
      "plugins/base-plugin"
    ]
  }
}


<!-- Source: plugin-code/agent-scaffolders/scripts/plugin_paths_whitelist.json -->
{
  "global_patterns": [
    "github\\.com/.*?/plugins/",
    "<APS_ROOT>/plugins/",
    "plugins/my-",
    "plugins/<",
    "# evaluate.py lives at plugins/",
    "plugins/adr-manager",
    "plugins/link-checker",
    "e\\.g\\. `?plugins/",
    "\\(e\\.g\\., `?plugins/",
    "claude-knowledgework-plugins/",
    "plugins/agent-agentic-os/skills/os-eval-runner/",
    "Users/robert/",
    "Users/jesse/",
    "Users/username/",
    "/Users/\\..*\\.",
    "e\\.g\\.,? /Users/",
    "RESOLVES TO: plugins/",
    "PLUGIN ROOT: plugins/",
    "FILE: plugins/",
    "plugins/plugin-installer",
    "plugins/MCP",
    "plugins/[A-Z]",
    "plugins/submit",
    "plugins/scripts/",
    "plugins/plugin-name",
    "plugins/formatter",
    "plugins/agent-scaffolders",
    "plugins/agent-agentic-os",
    "plugins/copilot-cli",
    "plugins/spec-kitty-plugin",
    "plugins/exploration-cycle-plugin",
    "plugins/agent-scaffolders",
    "plugins/[a-z-]+-plugin",
    "plugins/plugin-manager",
    "plugins/obsidian-integration",
    "plugins/rlm-factory",
    "<USER_HOME>/Projects/",
    "plugins/skills",
    "anthropics/knowledge-work-plugins/",
    "plugins/tool_inventory.json",
    "plugins/tools_manifest.json",
    "plugins/markdown",
    "plugins/investment-screener",
    "plugins/rsvp-speed-reader",
    "richfrem/agent-plugins-skills",
    "plugins/vector-db",
    "plugins/example_script.py",
    "plugins/task-manager",
    "@agent-plugins/",
    "plugins/ directory",
    "project's plugins/",
    "folder from plugins/",
    "maintain-plugins/"
  ],
  "file_specific_patterns": {
    "plugins/agent-agentic-os/assets/architecture-overview.md": [
      "  plugins/agent-agentic-os/          <- plugin source"
    ],
    "plugins/plugin-manager/references/plugin_replicator_overview.md": [
      "plugins/base-plugin"
    ]
  }
}


## See Also

- [[1-handle-absolute-paths-from-repo-root]]
- [[add-script-dir-to-path-to-import-plugin-inventory]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[adr-004-self-contained-plugins---no-cross-plugin-script-dependencies]]
- [[exploration-cycle-plugin-hooks]]
- [[install-plugin-in-a-different-repo-eg-context-bundler-specifically]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/fix-plugin-paths/scripts/plugin_paths_whitelist.json`
- **Indexed:** 2026-04-27T05:21:04.239617+00:00
