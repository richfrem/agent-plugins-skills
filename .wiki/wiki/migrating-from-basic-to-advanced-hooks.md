---
concept: migrating-from-basic-to-advanced-hooks
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-hook/references/migration.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.874952+00:00
cluster: command
content_hash: 0722f5bc6bf346e8
---

# Migrating from Basic to Advanced Hooks

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Migrating from Basic to Advanced Hooks

This guide shows how to migrate from basic command hooks to advanced prompt-based hooks for better maintainability and flexibility.

## Why Migrate?

Prompt-based hooks offer several advantages:

- **Natural language reasoning**: LLM understands context and intent
- **Better edge case handling**: Adapts to unexpected scenarios
- **No bash scripting required**: Simpler to write and maintain
- **More flexible validation**: Can handle complex logic without coding

## Migration Example: Bash Command Validation

### Before (Basic Command Hook)

**Configuration:**
```json
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "bash ./validate-bash.sh"
        }
      ]
    }
  ]
}
```

**Script (../scripts/validate-bash.sh):**
```bash
#!/bin/bash
input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command')

# Hard-coded validation logic
if [[ "$command" == *"rm -rf"* ]]; then
  echo "Dangerous command detected" >&2
  exit 2
fi
```

**Problems:**
- Only checks for exact "rm -rf" pattern
- Doesn't catch variations like `rm -fr` or `rm -r -f`
- Misses other dangerous commands (`dd`, `mkfs`, etc.)
- No context awareness
- Requires bash scripting knowledge

### After (Advanced Prompt Hook)

**Configuration:**
```json
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Command: $TOOL_INPUT.command. Analyze for: 1) Destructive operations (rm -rf, dd, mkfs, etc) 2) Privilege escalation (sudo) 3) Network operations without user consent. Return 'approve' or 'deny' with explanation.",
          "timeout": 15
        }
      ]
    }
  ]
}
```

**Benefits:**
- Catches all variations and patterns
- Understands intent, not just literal strings
- No script file needed
- Easy to extend with new criteria
- Context-aware decisions
- Natural language explanation in denial

## Migration Example: File Write Validation

### Before (Basic Command Hook)

**Configuration:**
```json
{
  "PreToolUse": [
    {
      "matcher": "Write",
      "hooks": [
        {
          "type": "command",
          "command": "bash ./validate-write.sh"
        }
      ]
    }
  ]
}
```

**Script (../scripts/validate-write.sh):**
```bash
#!/bin/bash
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path')

# Check for path traversal
if [[ "$file_path" == *".."* ]]; then
  echo '{"decision": "deny", "reason": "Path traversal detected"}' >&2
  exit 2
fi

# Check for system paths
if [[ "$file_path" == "/etc/"* ]] || [[ "$file_path" == "/sys/"* ]]; then
  echo '{"decision": "deny", "reason": "System file"}' >&2
  exit 2
fi
```

**Problems:**
- Hard-coded path patterns
- Doesn't understand symlinks
- Missing edge cases (e.g., `/etc` vs `/etc/`)
- No consideration of file content

### After (Advanced Prompt Hook)

**Configuration:**
```json
{
  "PreToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "File path: $TOOL_INPUT.file_path. Content preview: $TOOL_INPUT.content (first 200 chars). Verify: 1) Not system directories (/etc, /sys, /usr) 2) Not credentials (.env, tokens, secrets) 3) No path traversal 4) Content doesn't expose secrets. Return 'approve' or 'deny'."
        }
      ]
    }
  ]
}
```

**Benefits:**
- Context-aware (considers content too)
- Handles symlinks and edge cases
- Natural understanding of "system directories"
- Can detect secrets in content
- Easy to extend criteria

## When to Keep Command Hooks

Command hooks still have their place:

### 1. Deterministic Performance Checks

```bash
#!/bin/bash
# Check file size quickly
file_path=$(echo "$input" | jq -r '.tool_input.file_path')
size=$(stat -f%z "$file_path" 2>/dev/null || stat -c%s "$file_path" 2>/dev/null)

if [ "$size" -gt 10000000 ]; then
  echo '{"decision": "deny", "reason": "File too large"}' >&2
  exit 2
fi
```

**Use com

*(content truncated)*

## See Also

- [[sub-agents-hooks-and-commands]]
- [[memory-hygiene-when-to-write-promote-and-archive]]
- [[quickstart-how-to-run-an-optimization-loop-on-any-skill]]
- [[autoresearch-overview-applying-the-karpathy-loop-to-any-target]]
- [[meta-harness-end-to-end-optimization-of-model-harnesses]]
- [[sub-agents-and-hooks]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-hook/references/migration.md`
- **Indexed:** 2026-04-17T06:42:09.874952+00:00
