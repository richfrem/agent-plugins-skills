---
name: create-hook
description: >
  This skill should be used when the user asks to "create a hook", "add a hook",
  "add a PreToolUse hook", "add a Stop hook", "validate tool use", "implement a
  prompt-based hook", "set up event-driven automation", "block dangerous commands",
  "run something on session start", or mentions any hook event (PreToolUse,
  PostToolUse, Stop, SubagentStop, SessionStart, SessionEnd, UserPromptSubmit,
  PreCompact, Notification). Use this skill whenever hooks are mentioned even if
  the user doesn't say the word "hook" explicitly -- e.g. "run a script before
  Claude writes files" or "validate commands before execution" should trigger this.
  Do NOT use this for creating skills (use create-skill) or sub-agents (use create-sub-agent).
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---

# Hook Development for Claude Code Plugins

Hooks are event-driven automation that execute in response to Claude Code events.
Use them to validate operations before they run, react to results, enforce policies,
add context, and integrate external tools into the agent workflow.

> Reference files: `references/patterns.md` (8+ proven patterns), `references/advanced.md`
> (advanced use cases), `references/migration.md` (upgrading basic hooks). Example
> scripts in `examples/`. Validation utilities in `scripts/`.

---

## Step 1: Understand the Use Case

Ask only what is still unclear. Extract from context first.

**Core questions:**

1. **Which event?** Choose based on when the hook should fire:

   | Event | When | Primary Use |
   |-------|------|-------------|
   | `PreToolUse` | Before any tool runs | Approve, deny, or modify tool calls |
   | `PostToolUse` | After tool completes | Feedback, logging, react to results |
   | `UserPromptSubmit` | When user submits a prompt | Add context, validate, block |
   | `Stop` | When main agent considers stopping | Completeness check |
   | `SubagentStop` | When subagent considers stopping | Task validation |
   | `SessionStart` | Session begins | Load context, set environment |
   | `SessionEnd` | Session ends | Cleanup, logging, state preservation |
   | `PreCompact` | Before context compaction | Preserve critical context |
   | `Notification` | Claude sends notification | Logging, reactions |

2. **Hook type -- prompt or command?**
   - **Prompt-based** (recommended): LLM-driven context-aware decisions. Flexible,
     good for semantic reasoning, validation, complex edge cases. Use for PreToolUse,
     Stop, UserPromptSubmit.
   - **Command**: Deterministic bash execution. Fast, reliable, no LLM latency. Use
     for quick validation, file checks, external integrations.

3. **Matcher**: Which tools should trigger it?
   - Exact: `"Write"` or `"Bash"`
   - Multiple: `"Write|Edit|Read"`
   - All tools: `"*"`
   - Regex: `"mcp__.*__delete.*"` (all MCP delete tools)
   - Note: matchers are case-sensitive.

4. **What should it do?** And what's the desired output?
   - Allow/deny/ask? (`permissionDecision`)
   - Approve/block? (Stop events: `decision: "approve" | "block"`)
   - Pass info to Claude? (`systemMessage`)

5. **Placement**: Plugin (`hooks/hooks.json`) or user settings (`.claude/settings.json`)?

---

## Step 2: Choose the Right Hook Type

**Prompt-based hooks** (prefer these):
```json
{
  "type": "prompt",
  "prompt": "Evaluate if this tool use is appropriate: $TOOL_INPUT",
  "timeout": 30
}
```
Benefits: context-aware, no bash scripting, easier to maintain, better edge cases.

**Command hooks** (for deterministic/fast checks):
```json
{
  "type": "command",
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh",
  "timeout": 60
}
```
Always use `${CLAUDE_PLUGIN_ROOT}` for portability -- never hardcode paths.
Default timeouts: command (60s), prompt (30s).

---

## Step 3: Design the Hook Configuration

### Plugin hooks.json format (for plugin hooks):
```json
{
  "description": "Brief explanation (optional)",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Validate file write safety. Check: system paths, credentials, path traversal, sensitive content. Return 'approve' or 'deny'."
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Verify task completion: tests run, build succeeded, questions answered. Return 'approve' to stop or 'block' with reason to continue."
          }
        ]
      }
    ]
  }
}
```

### Settings format (for `.claude/settings.json` -- no wrapper):
```json
{
  "PreToolUse": [...],
  "Stop": [...]
}
```

### Hook output format:
All hooks output JSON to stdout:
```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Message for Claude"
}
```

**PreToolUse-specific output:**
```json
{
  "hookSpecificOutput": {
    "permissionDecision": "allow|deny|ask",
    "updatedInput": {"field": "modified_value"}
  },
  "systemMessage": "Explanation for Claude"
}
```

**Stop/SubagentStop output:**
```json
{
  "decision": "approve|block",
  "reason": "Explanation",
  "systemMessage": "Additional context"
}
```

**Exit codes:**
- `0` -- success (stdout shown in transcript)
- `2` -- blocking error (stderr fed back to Claude)
- Other -- non-blocking error

### Hook input (available in command hooks via stdin):
```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.txt",
  "cwd": "/current/working/dir",
  "hook_event_name": "PreToolUse",
  "tool_name": "Write",
  "tool_input": {...}
}
```
Access in prompt hooks via: `$TOOL_INPUT`, `$TOOL_RESULT`, `$USER_PROMPT`.

---

## Step 4: Implement the Hook

### For command hooks, write the script
Use `scripts/validate-write.sh`, `scripts/validate-bash.sh`, or
`scripts/load-context.sh` as starting templates.

**Security non-negotiables for every command hook:**
```bash
#!/bin/bash
set -euo pipefail  # fail fast, no unset variables

input=$(cat)       # read stdin once
tool_name=$(echo "$input" | jq -r '.tool_name')   # quote all variables
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

# Block path traversal
if [[ "$file_path" == *".."* ]]; then
  echo '{"decision": "deny", "reason": "Path traversal detected"}' >&2
  exit 2
fi

# Block sensitive files
if [[ "$file_path" == *".env"* ]]; then
  echo '{"decision": "deny", "reason": "Sensitive file access blocked"}' >&2
  exit 2
fi
```

**SessionStart -- persist env vars:**
```bash
# Persist variables for the session
echo "export PROJECT_TYPE=nodejs" >> "$CLAUDE_ENV_FILE"
```

**Conditional/temporary hooks (flag file pattern):**
```bash
FLAG_FILE="$CLAUDE_PROJECT_DIR/.enable-strict-validation"
if [ ! -f "$FLAG_FILE" ]; then
  exit 0  # hook disabled, skip silently
fi
# ... validation logic ...
```

### Environment variables available in command hooks:
- `$CLAUDE_PROJECT_DIR` -- project root path
- `$CLAUDE_PLUGIN_ROOT` -- plugin directory (use for all file references)
- `$CLAUDE_ENV_FILE` -- SessionStart only: write env exports here
- `$CLAUDE_CODE_REMOTE` -- set when running in remote context

### Parallel execution -- design for independence:
All matching hooks in a list run **in parallel**. They cannot see each other's output
and execution order is non-deterministic. Each hook must be fully self-contained.

---

## Step 5: Validate and Test

**Validate the hooks.json schema:**
```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate-hook-schema.sh hooks/hooks.json
```

**Test a command hook directly:**
```bash
echo '{"tool_name": "Write", "tool_input": {"file_path": "/test"}}' | \
  bash hooks/validate-write.sh
echo "Exit code: $?"
```

**Full integration test via the test-hook script:**
```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/test-hook.sh \
  --hook hooks/validate-write.sh \
  --event PreToolUse \
  --input '{"tool_name": "Write", "tool_input": {"file_path": "src/app.py"}}'
```

**Lint hook scripts for common issues:**
```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/hook-linter.sh hooks/
```

**Test in Claude Code with debug output:**
```bash
claude --debug
```
Look for: hook registration, execution logs, input/output JSON, timing.

**CRITICAL: Hooks require Claude Code restart to take effect.**
After editing `hooks/hooks.json` or hook scripts:
1. Exit Claude Code
2. Restart: `claude` or `cc`
3. Verify with `/hooks` command in the session

---

## Step 6: Document and Finalize

- Document the hook's activation mechanism in the plugin README
- For temporary/conditional hooks, document how to enable/disable them
- For sensitive hooks (blocking, denying), explain what gets blocked and why
- Validate with `audit-plugin` to check overall plugin structure

---

## Quick Decision Guide

```
Need to validate before a tool runs?         -> PreToolUse with prompt hook
Need deterministic fast validation?          -> PreToolUse with command hook
Need complex reasoning about file safety?    -> Prompt-based PreToolUse
Need to ensure Claude completes the task?    -> Stop with prompt hook
Need to load project context at start?       -> SessionStart with command hook
Need to react to tool output?                -> PostToolUse
Need to enrich user prompts with context?    -> UserPromptSubmit
Need the hook to be togglable?               -> Flag file pattern
Need to preserve info across context compact? -> PreCompact
```

---

## Reference Files

Read these when needed:
- `references/patterns.md` -- 8+ proven hook patterns (security validator, completeness checker, context loader, etc.)
- `references/advanced.md` -- advanced techniques: MCP integration, multi-hook orchestration, stateful hooks
- `references/migration.md` -- migrating from basic command hooks to advanced prompt-based hooks
- `scripts/validate-write.sh` -- complete file write validation example
- `scripts/validate-bash.sh` -- complete bash command validation example
- `scripts/load-context.sh` -- complete SessionStart context loading example
- Official docs: https://docs.claude.com/en/docs/claude-code/hooks
