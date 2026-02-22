# Hooks Research

This document captures our accumulated knowledge and definitive specifications for **Hooks**.

**Source:** [Hooks reference](https://code.claude.com/docs/en/hooks)

## Definition
Hooks are user-defined shell commands, LLM prompts, or multi-turn agent scripts that run automatically during specific events in the Claude Code lifecycle. They allow for automating workflows, enforcing policies, or customizing Claude Code's behavior.

## Hook Lifecycle and Events
Hooks fire based on lifecycle events. The available events are:

1. **SessionStart**: When session starts/resumes/clears/compacts.
2. **UserPromptSubmit**: Before Claude processes a user prompt.
3. **PreToolUse**: Before a tool runs (can allow/deny/ask).
4. **PermissionRequest**: When a permission dialog is shown (can allow/deny).
5. **PostToolUse**: After successful tool execution.
6. **PostToolUseFailure**: After a tool fails.
7. **Notification**: On system notifications (idle, permission).
8. **SubagentStart**: When a subagent spawns (Task tool).
9. **SubagentStop**: When a subagent finishes.
10. **Stop**: When the main Claude Code agent finishes responding.
11. **TeammateIdle**: Before an agent goes idle.
12. **TaskCompleted**: Before a task is marked complete.
13. **ConfigChange**: When a configuration file changes.
14. **PreCompact**: Before context compaction.
15. **SessionEnd**: When the session terminates.

## Configuration & Structure
Hooks are configured in `hooks.json` files or inline within `plugin.json`, `SKILL.md`, or agent frontmatter.

The general nested structure in JSON:
1. Selection of a Hook Event (e.g. `"PreToolUse"`).
2. Definition of a Matcher (regex filtering on the tool name, session start type, etc. e.g. `"matcher": "Bash"`).
3. Array of Hooks to execute.

Available hook `"type"` properties:
- `"command"`: Runs a shell command.
- `"prompt"`: Sends a prompt to a Claude model for a single-turn evaluation.
- `"agent"`: Spawns a subagent to evaluate conditions using tools.

## Input & Output Handling
- Hooks receive JSON context on `stdin`.
- Common input fields include: `session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`.
- Events pass additional specific fields depending on the event (e.g. `tool_name` for tool events).

### Exit Codes and JSON Output
- **Exit 0 (Success)**: Claude Code parses `stdout` for a JSON object with structured control fields. If no JSON is provided, plain text is ignored or added to context (for some events).
- **Exit 2 (Blocking Error)**: The action is blocked (if blockable), and `stderr` is passed back as feedback or an error message.

### Output JSON Properties
When returning Exit 0 with a JSON object, hooks can return:
- **Universal Decision Fields**:
```json
{
  "continue": false, // stop the processing
  "stopReason": "Build Failed", // message to the user
  "decision": "block", // block action from continuing
  "reason": "Test suite failed" // reason
}
```

- **Hook-Specific output** (for events like `PreToolUse`, `PermissionRequest`):
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow", // allow, deny, ask
    "permissionDecisionReason": "Checking passed",
    "updatedInput": { "command": "npm run lint" },
    "additionalContext": "Current environment: production."
  }
}
```

## Environment Variables
- `$CLAUDE_PROJECT_DIR`: Points to the current project's root.
- `${CLAUDE_PLUGIN_ROOT}`: Points to the root directory of the plugin executing the hook. (Extremely important for referencing internal plugin scripts).
- `$CLAUDE_ENV_FILE`: Specific to `SessionStart` hooks to persist environment variables across future Bash commands in the session.

## Async Execution
Command hooks (`type: "command"`) can run in the background by setting `"async": true`. They cannot block or control Claude's behavior because the main process moves on immediately. Output can be delivered on the next turn via `systemMessage` or `additionalContext`.

## Security Considerations
Hooks run with the system user's full permissions. Use absolute paths (`$CLAUDE_PROJECT_DIR`), block path traversal (`..`), quote shell variables, and avoid exposing sensitive files.

## Debugging
Run `claude --debug` or `/debug` in TUI to view detailed hook execution states and failures. Parse errors will be flagged if standard output prints non-JSON items on Exit 0.
