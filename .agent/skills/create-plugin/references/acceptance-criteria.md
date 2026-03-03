# Acceptance Criteria: create-plugin

**Purpose**: Verify the system generates compliant root `.claude-plugin` architectures.

## 1. Directory Structure
- **[PASSED]**: Generates `skills/`, `agents/`, `commands/`, and nested `hooks/scripts/` folders.
- **[FAILED]**: Fails to create the base directories or puts scripts in root.

## 2. Configuration Files
- **[PASSED]**: Generates an `.mcp.json` and a `.claude-plugin/plugin.json` manifest.
- **[FAILED]**: Names the file `mcp.json` (missing dot) or fails to generate the manifest.
