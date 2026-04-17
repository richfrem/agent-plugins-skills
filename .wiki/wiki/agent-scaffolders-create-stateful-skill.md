---
concept: agent-scaffolders-create-stateful-skill
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/agent-scaffolders_create-stateful-skill.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.319130+00:00
cluster: state
content_hash: e63d385ed5d61130
---

# Agent Scaffolders Create Stateful Skill

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: create-stateful-skill
description: Scaffold an advanced stateful agent skill with L4 patterns
argument-hint: "[skill-name]"
allowed-tools: Bash, Read, Write
---

Follow the `create-stateful-skill` skill workflow to scaffold an advanced agent skill
with L4 state management, lifecycle artifacts, and chained commands.

## Inputs

- `$ARGUMENTS` — optional skill name or use-case description. Omit to start with discovery.

## Steps

1. If `$ARGUMENTS` provides a skill name or context, use it to seed discovery
2. Follow the create-stateful-skill phased workflow: confirm which L4 patterns are needed
   (state management, lifecycle artifacts, tone configuration, chained commands,
   escalation taxonomy), design the state schema and lifecycle checkpoints, then
   scaffold the skill directory with full L4 scaffolding
3. Report created skill path and explain the state management strategy

## Output

Skill directory with `SKILL.md` implementing selected L4 patterns, state schema,
lifecycle artifact templates, and chained command definitions.

## Edge Cases

- If `$ARGUMENTS` is empty: begin with discovery — identify which L4 patterns apply
- If the use case is simple (no persistent state, no chaining): recommend `create-skill`
  instead — stateful scaffolding adds complexity that simple skills don't need
- If the workflow requires human checkpoints: design explicit escalation taxonomy steps


## See Also

- [[agent-scaffolders-create-docker-skill]]
- [[agent-scaffolders-create-docker-skill]]
- [[procedural-fallback-tree-create-stateful-skill]]
- [[procedural-fallback-tree-create-stateful-skill]]
- [[procedural-fallback-tree-create-stateful-skill]]
- [[agent-scaffolders-create-agentic-workflow]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/agent-scaffolders_create-stateful-skill.md`
- **Indexed:** 2026-04-17T06:42:10.319130+00:00
