---
concept: acceptance-criteria-tool-inventory-init
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/tool-inventory-init/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.266394+00:00
cluster: agent
content_hash: b2933d839da5719a
---

# Acceptance Criteria: Tool Inventory Init

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: Tool Inventory Init

## Objective
Ensure the Agent can correctly scaffold the initial repository configurations for RLM tool caching.

## Scenario 1: Initializing the Profile
- **Setup**: Agent is asked to initialize the tool inventory for a new project.
- **Action**: The Agent executes `../scripts/tool_inventory_init.py`.
- **Validation**: The script creates `.agent/learning/rlm_profiles.json` and a `tools` profile exists defining the extensions to `.py` and `.js`.

## Scenario 2: Manifest Generation 
- **Setup**: Agent runs the initialization script on a fresh repo.
- **Action**: The script successfully creates the manifest files.
- **Validation**: `.agent/learning/rlm_tools_manifest.json` exists and includes the `plugins/` and `plugins/` globs for recursive searching, explicitly excluding `node_modules` and `.venv`.


## See Also

- [[acceptance-criteria-tool-inventory]]
- [[acceptance-criteria-tool-inventory]]
- [[acceptance-criteria-os-init]]
- [[acceptance-criteria-hf-init]]
- [[acceptance-criteria-obsidian-init]]
- [[acceptance-criteria-rlm-init]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/tool-inventory-init/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.266394+00:00
