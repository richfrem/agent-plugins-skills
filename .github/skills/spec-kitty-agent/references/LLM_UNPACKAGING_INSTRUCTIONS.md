# Spec Kitty Bridge: Unpackaging Instructions

## Purpose
This bundle contains the complete toolset for the "Universal Bridge" capability in the Spec Kitty framework. It includes Python scripts, documentation, skill definitions, and agent workflows.

## Contents
The bundle includes files for the following directories:
1.  `plugins/bridge/` - The core Python scripts and documentation.
2.  `.agent/skills/spec-kitty-bridge/` - The skill definition for AI agents.
3.  `.agent/workflows/utilities/` - The user-facing workflow trigger.

## Instructions for AI Agent

To unpackage and install this capability:

1.  **Extract Files**: Read the file paths from the bundle header and write the content to the corresponding absolute paths in the workspace. Ensure parent directories are created if they don't exist.

2.  **Make Executable**: Ensure the Python scripts in `plugins/bridge/` are executable:
    ```bash
    chmod +x plugins/bridge/*.py
    ```

3.  **Verify Installation**:
    Run the integrity check to confirm the bridge is operational:
    ```bash
    python3 plugins/spec-kitty/scripts/verify_bridge_integrity.py
    ```

4.  **Register Tools**:
    Access `plugins/bridge/tool_inventory.json` (included in this bundle) to see the list of tools available for registration in your agent's configuration.

5.  **Restart IDE**:
    If this is a fresh install, restart the IDE to load the new slash commands (e.g., `/spec-kitty.bridge`).
