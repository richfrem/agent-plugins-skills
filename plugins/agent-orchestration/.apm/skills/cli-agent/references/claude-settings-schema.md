# Claude Code `settings.json` Schema Reference

Source: https://code.claude.com/docs/en/settings

## Minimal Recommended `settings.json`

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  }
}
```

## Key Settings

| Key | Description | Example |
|-----|-------------|---------|
| `permissions.allow` | Tool use allowed without prompting | `["Bash(npm test *)", "Bash(git diff *)"]` |
| `permissions.deny` | Blocked tool use | `["Bash(rm -rf *)", "Read(./.env)"]` |
| `permissions.ask` | Require confirmation | `["Bash(git push *)"]` |
| `hooks` | Lifecycle event scripts | `{ "PostToolUse": [...] }` |
| `model` | Default model override | `"claude-sonnet-4-6"` |
| `env` | Environment variables for every session | `{"FOO": "bar"}` |
| `outputStyle` | Custom system-prompt style | `"Explanatory"` |
| `includeGitInstructions` | Include built-in git workflow instructions | `false` |

## Permission Rule Syntax

| Pattern | Matches |
|---------|---------|
| `Bash` | All bash commands |
| `Bash(npm run *)` | Commands starting with `npm run` |
| `Read(./.env)` | Reading the `.env` file |
| `Read(./secrets/**)` | Any file under secrets/ |
| `WebFetch(domain:example.com)` | Fetch to example.com |

Rules eval order: **deny first, then ask, then allow**. First match wins.

## Hooks Format

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "npx prettier --write $CLAUDE_TOOL_INPUT_FILE_PATH"
      }]
    }],
    "SessionStart": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "python .agents/hooks/session_start.py"
      }]
    }]
  }
}
```

## Common Hook Events
- `PreToolUse` — before any tool call
- `PostToolUse` — after any tool call  
- `SessionStart` — at the start of every session
- `Stop` — when Claude finishes a turn

## Excluding Sensitive Files

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(./config/credentials.json)"
    ]
  }
}
```
