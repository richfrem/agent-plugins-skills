# Acceptance Criteria: audit-plugin

**Purpose**: Verify the system auditor accurately detects specification failures.

## 1. File Detection
- **[PASSED]**: Auditor throws an error if `plugin.json` or `.claude-plugin/` directory is missing.
- **[FAILED]**: Auditor silently passes a plugin that stores its `hooks.json` in the root directory instead of `hooks/hooks.json`.

## 2. Script Restriction  
- **[PASSED]**: Auditor strictly rejects any `.sh` or `.ps1` files residing in `skills/*/scripts/`.
- **[FAILED]**: Auditor allows a bash script to exist inside a skill's dedicated execution directory.
