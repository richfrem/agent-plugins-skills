---
concept: agent-scaffolders-create-hook
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/agent-scaffolders_create-hook.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.318200+00:00
cluster: event
content_hash: a9583c59cadacb2c
---

# Agent Scaffolders Create Hook

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
3. Validate with `validate-hook-schema.sh` and test with `test-hook.sh`
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


## See Also

- [[agent-scaffolders-create-agentic-workflow]]
- [[agent-scaffolders-create-azure-agent]]
- [[agent-scaffolders-create-docker-skill]]
- [[agent-scaffolders-create-github-action]]
- [[agent-scaffolders-create-mcp-integration]]
- [[agent-scaffolders-create-plugin]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/agent-scaffolders_create-hook.md`
- **Indexed:** 2026-04-17T06:42:10.318200+00:00
