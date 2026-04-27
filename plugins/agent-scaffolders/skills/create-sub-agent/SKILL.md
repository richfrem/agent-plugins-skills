---
name: create-sub-agent
plugin: agent-scaffolders
description: Design and scaffold a Claude Code sub-agent
argument-hint: "[agent-name or use-case description]"
allowed-tools: Bash, Read, Write
---

Follow the `create-sub-agent` skill workflow to design and generate a Claude Code agent file.

## Inputs

- `$ARGUMENTS` — optional agent name or brief use-case description passed as initial context
  to the design interview. Omit to start with open discovery.

## Steps

1. If `$ARGUMENTS` is provided, use it as the starting context for agent name / purpose
2. Follow the create-sub-agent phased workflow: extract core intent via design interview
   (purpose, input/output contract, escalation posture, tools, permissions.deny, model,
   maxTokens, color, lifecycle hooks, placement), present design summary, confirm,
   then generate the agent `.md` file
3. Validate the generated agent with `validate_agent.py`
4. Report the created agent path, triggering conditions, and next steps

## Output

Agent `.md` file with complete YAML frontmatter (name, description with `<example>` blocks,
model, maxTokens, color, permissions.allowedTools, permissions.deny) and a second-person
system prompt targeting 500-3,000 characters.

## Placement Rules

**Plugin agents**: flat `.md` file — `plugins/<plugin-name>/agents/<agent-name>.md`
- **No subdirectory.** Skills use `skills/<name>/SKILL.md` subdirectory format, but agents do NOT.
- Confirmed against Anthropic official plugins (`feature-dev`, `code-simplifier`, `hookify`).

**Local/project agents**: `.claude/agents/<agent-name>.md` (also flat, no subdirectory).

## Edge Cases

- If `$ARGUMENTS` is empty: conduct the full Phase 1 design interview — do not pre-fill
- If an agent with that name already exists: confirm before overwriting
- If requirements suggest multiple responsibilities: propose splitting into specialized agents
- If high-risk operations are required: configure escalation posture and add Stop hook
