# Spec Kitty Bridge: Unpackaging Instructions

## Purpose
This bundle contains the complete toolset for the "Universal Bridge" capability in the Spec Kitty framework. It includes Python scripts, documentation, skill definitions, and agent workflows.

## Contents
The bundle includes files for the following directories:
1.  `bridge/` - The core Python scripts and documentation.
2.  `.agents/skills/spec-kitty-bridge/` - The skill definition for AI agents.
3.  `.agents/workflows/utilities/` - The user-facing workflow trigger.

## Instructions for AI Agent

To unpackage and install this capability:

1.  **Extract Files**: Read the file paths from the bundle header and write the content to the corresponding absolute paths in the workspace. Ensure parent directories are created if they don't exist.

2.  **Install via Bridge**: Trigger the `plugin-manager:plugin-installer` skill to install the bridge capability into the active agent environment. The skill handles file placement and permissions.

3.  **Verify Installation**:
    Trigger the `spec-kitty-plugin:spec-kitty-sync-plugin` skill to confirm the bridge is operational.

4.  **Register Tools**:
    Access `bridge/plugins/tool_inventory.json` (included in this bundle) to see the list of tools available for registration in your agent's configuration.

5.  **Restart IDE**:
    If this is a fresh install, restart the IDE to load the new slash commands (e.g., `/spec-kitty.bridge`).
