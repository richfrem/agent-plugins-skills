# Acceptance Criteria: create-hook

**Purpose**: Verify the system generates compliant `hooks/hooks.json` lifecycle interceptors.

## 1. Event Registration
- **[PASSED]**: Appends a new hook trigger listening to `PreToolUse` or `PostToolUse` directly in the plugin's `hooks.json` array.
- **[FAILED]**: Fails to create the JSON syntax correctly or overrides previous hooks instead of appending.
