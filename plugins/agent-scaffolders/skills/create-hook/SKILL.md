---
name: create-hook
plugin: agent-scaffolders
description: >
  Scaffolds a new event-driven hook in a plugin. NOT for creating interactive slash commands (use `create-command`) and NOT for GitHub Actions agentic workflows (use `create-agentic-workflow`).
argument-hint: "[event-type or use case]"
allowed-tools: Bash, Read, Write
---

Follow the `create-hook` skill workflow to design and generate a hook configuration.

## Inputs

- `$ARGUMENTS` — optional hook event type (e.g. `PreToolUse`, `Stop`, `PermissionRequest`)
  or a use-case description (e.g. "block dangerous bash commands"). Omit for discovery.

## Steps

1. If `$ARGUMENTS` names an event or use case, use it to seed Phase 1 questions
2. Follow the create-hook phased workflow: select event, choose handler type
   (command / prompt / agent), design the matcher and logic, then write the hook entry
3. Validate with `validate_hook_schema.py` and test with `test_hook.py`
4. Report placement (global `hooks.json` vs skill-scoped frontmatter) and next steps

## Output

`hooks.json` entry or SKILL.md frontmatter block with complete hook configuration
(event, matcher, handler type, command/prompt body, output schema).

## Hook Script Standards

When generating a Python hook script, always apply these two rules:

**Cross-platform python command** — use `python3 ... || python ...` in hooks.json so the hook works on both macOS/Linux (python3) and Windows (python):
```json
{ "type": "command", "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/script.py || python ${CLAUDE_PLUGIN_ROOT}/hooks/script.py" }
```

**Project-type guard** — hooks run in every project, not just ones that have initialized this plugin. Add an early-exit guard at the top of `main()` so the script skips silently in projects that lack the required context:
```python
def main():
    project_root = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    if not (project_root / "context").exists():
        return  # Not an initialized project — skip silently
    ...
```
Adapt the guard to whatever directory/file your hook requires (e.g. `.agent/`, `context/os-state.json`).

## Edge Cases

- If `$ARGUMENTS` is empty: begin with the event selection question in Phase 1
- If the requested event is not in the 13 supported events: explain valid options
- If the use case implies a skill-scoped hook (enforce invariant only during one skill):
  generate frontmatter syntax instead of a global hooks.json entry
- If user wants to auto-approve subagent permissions: use PermissionRequest + prompt handler
