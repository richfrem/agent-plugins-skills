---
concept: common-hook-patterns
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-hook/references/patterns.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.895629+00:00
cluster: pattern
content_hash: 622584da6c3d86d9
---

# Common Hook Patterns

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Common Hook Patterns

This reference provides common, proven patterns for implementing Claude Code hooks. Use these patterns as starting points for typical hook use cases.

## Pattern 1: Security Validation

Block dangerous file writes using prompt-based hooks:

```json
{
  "PreToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "File path: $TOOL_INPUT.file_path. Verify: 1) Not in /etc or system directories 2) Not .env or credentials 3) Path doesn't contain '..' traversal. Return 'approve' or 'deny'."
        }
      ]
    }
  ]
}
```

**Use for:** Preventing writes to sensitive files or system directories.

## Pattern 2: Test Enforcement

Ensure tests run before stopping:

```json
{
  "Stop": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Review transcript. If code was modified (Write/Edit tools used), verify tests were executed. If no tests were run, block with reason 'Tests must be run after code changes'."
        }
      ]
    }
  ]
}
```

**Use for:** Enforcing quality standards and preventing incomplete work.

## Pattern 3: Context Loading

Load project-specific context at session start:

```json
{
  "SessionStart": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/./load-context.sh"
        }
      ]
    }
  ]
}
```

**Example script (../scripts/load-context.sh):**
```bash
#!/bin/bash
cd "$CLAUDE_PROJECT_DIR" || exit 1

# Detect project type
if [ -f "package.json" ]; then
  echo "📦 Node.js project detected"
  echo "export PROJECT_TYPE=nodejs" >> "$CLAUDE_ENV_FILE"
elif [ -f "Cargo.toml" ]; then
  echo "🦀 Rust project detected"
  echo "export PROJECT_TYPE=rust" >> "$CLAUDE_ENV_FILE"
fi
```

**Use for:** Automatically detecting and configuring project-specific settings.

## Pattern 4: Notification Logging

Log all notifications for audit or analysis:

```json
{
  "Notification": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/log-notification.sh"
        }
      ]
    }
  ]
}
```

**Use for:** Tracking user notifications or integration with external logging systems.

## Pattern 5: MCP Tool Monitoring

Monitor and validate MCP tool usage:

```json
{
  "PreToolUse": [
    {
      "matcher": "mcp__.*__delete.*",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Deletion operation detected. Verify: Is this deletion intentional? Can it be undone? Are there backups? Return 'approve' only if safe."
        }
      ]
    }
  ]
}
```

**Use for:** Protecting against destructive MCP operations.

## Pattern 6: Build Verification

Ensure project builds after code changes:

```json
{
  "Stop": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Check if code was modified. If Write/Edit tools were used, verify the project was built (npm run build, cargo build, etc). If not built, block and request build."
        }
      ]
    }
  ]
}
```

**Use for:** Catching build errors before committing or stopping work.

## Pattern 7: Permission Confirmation

Ask user before dangerous operations:

```json
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Command: $TOOL_INPUT.command. If command contains 'rm', 'delete', 'drop', or other destructive operations, return 'ask' to confirm with user. Otherwise 'approve'."
        }
      ]
    }
  ]
}
```

**Use for:** User confirmation on potentially destructive commands.

## Pattern 8: Code Quality Checks

Run linters or formatters on file edits:

```json
{
  "PostToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "command",
          "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/check-qu

*(content truncated)*

## See Also

- [[context-folder-patterns]]
- [[optimizer-engine-patterns-reference-design]]
- [[optimizer-engine-patterns-reference-design]]
- [[context-folder-patterns]]
- [[context-folder-patterns]]
- [[optimizer-engine-patterns]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-hook/references/patterns.md`
- **Indexed:** 2026-04-17T06:42:09.895629+00:00
