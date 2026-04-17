---
concept: procedural-fallback-tree-coding-conventions
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/coding-conventions-agent/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.747772+00:00
cluster: language
content_hash: da0fbd80033fec14
---

# Procedural Fallback Tree: Coding Conventions

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Coding Conventions

## 1. File Header Template Missing for Language
If a language's header format is not in the skill (e.g., a new language is introduced):
- **Action**: Use the closest existing template as a structural base. Report that no official template exists for the language and ask the user to ratify the adapted template before committing it as the standard.

## 2. Function Exceeds 50-Line Threshold Mid-Implementation
If a function being written grows beyond 50 lines:
- **Action**: STOP adding to the function. Extract the oversized block into a named helper. Resume writing only after the refactor. Do NOT finish the long function and "plan to refactor later."

## 3. New Script Not Registered in tool_inventory.json
If a new script in plugins/ is missing from tool_inventory.json after creation:
- **Action**: Trigger the `tool-inventory` skill to register the script. Do NOT commit the script without the registration. Ask the agent to confirm 0 untracked scripts before staging.

## 4. Ambiguous Naming Convention (Multi-Language File)
If a file or function spans multiple language contexts (e.g., a Python script calling TypeScript-style names from a schema):
- **Action**: Apply the target file's language convention. Report the ambiguity to the user and note which convention was applied. Never mix conventions within a single file.


## See Also

- [[procedural-fallback-tree-adr-management]]
- [[procedural-fallback-tree-agent-swarm]]
- [[procedural-fallback-tree-dual-loop]]
- [[procedural-fallback-tree-learning-loop]]
- [[procedural-fallback-tree-orchestrator-routing]]
- [[procedural-fallback-tree-red-team-review]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/coding-conventions-agent/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:09.747772+00:00
