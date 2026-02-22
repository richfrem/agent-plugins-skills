# Acceptance Criteria: Tool Inventory Init

## Objective
Ensure the Agent can correctly scaffold the initial repository configurations for RLM tool caching.

## Scenario 1: Initializing the Profile
- **Setup**: Agent is asked to initialize the tool inventory for a new project.
- **Action**: The Agent executes `tool_inventory_init.py`.
- **Validation**: The script creates `.agent/learning/rlm_profiles.json` and a `tools` profile exists defining the extensions to `.py` and `.js`.

## Scenario 2: Manifest Generation 
- **Setup**: Agent runs the initialization script on a fresh repo.
- **Action**: The script successfully creates the manifest files.
- **Validation**: `.agent/learning/rlm_tools_manifest.json` exists and includes the `plugins/` and `plugins/` globs for recursive searching, explicitly excluding `node_modules` and `.venv`.
