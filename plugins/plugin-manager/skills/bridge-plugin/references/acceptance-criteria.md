# Acceptance Criteria: agent-bridge

**Purpose**: Verify the Universal System Bridger executes and maps components accurately.

## 1. Explicit Target Selection
- **[PASSED]**: When invoked with `--target antigravity`, the bridge successfully deploys logic strictly to `.agent/workflows/` and `.agent/skills/`.
- **[FAILED]**: When invoked, the bridge assumes `--target auto` and scatters plugin data across `.claude`, `.gemini`, `.github`, and `.agent` even when the user only wants it in one IDE.

## 2. Directory Separation 
- **[PASSED]**: Logic residing in `plugins/<name>/skills/` is deployed to `.agent/skills/`. Logic residing in `plugins/<name>/commands/` is deployed to `.agent/workflows/`.
- **[FAILED]**: Logic residing in `commands/` is mixed into `.agent/skills/`, duplicating context.
