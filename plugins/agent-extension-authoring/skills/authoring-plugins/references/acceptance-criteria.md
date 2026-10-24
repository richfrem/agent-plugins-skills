# Acceptance Criteria: authoring-plugins

Merged verbatim from the retired skills; one section per mode.

## Mode: create-plugin

**Purpose**: Verify the system generates compliant root `.claude-plugin` architectures.

## 1. Directory Structure
- **[PASSED]**: Generates `skills/`, `agents/`, `commands/`, and nested `hooks/scripts/` folders.
- **[FAILED]**: Fails to create the base directories or puts scripts in root.

## 2. Configuration Files
- **[PASSED]**: Generates an `.mcp.json` and a `.claude-plugin/plugin.json` manifest.
- **[FAILED]**: Names the file `mcp.json` (missing dot) or fails to generate the manifest.

## Mode: audit-plugin

**Purpose**: Verify the system auditor accurately detects specification failures.

## 1. File Detection
- **[PASSED]**: Auditor throws an error if `../../../.claude-plugin/plugin.json` or `.claude-plugin/` directory is missing.
- **[FAILED]**: Auditor silently passes a plugin that stores its `hooks.json` in the root directory instead of `hooks/hooks.json`.

## 2. Script Restriction  
- **[PASSED]**: Auditor strictly rejects any `.sh` or `.ps1` files residing in `skills/*/scripts/`.
- **[FAILED]**: Auditor allows a bash script to exist inside a skill's dedicated execution directory.
