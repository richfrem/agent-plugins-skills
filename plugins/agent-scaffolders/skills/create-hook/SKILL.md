---
name: create-hook
description: Design and scaffold an event-driven Claude Code hook
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

## Edge Cases

- If `$ARGUMENTS` is empty: begin with the event selection question in Phase 1
- If the requested event is not in the 13 supported events: explain valid options
- If the use case implies a skill-scoped hook (enforce invariant only during one skill):
  generate frontmatter syntax instead of a global hooks.json entry
- If user wants to auto-approve subagent permissions: use PermissionRequest + prompt handler
