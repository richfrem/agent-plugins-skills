---
concept: procedural-fallback-tree-create-azure-agent
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-azure-agent/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.777848+00:00
cluster: user
content_hash: 4bc588bdae0e6f9b
---

# Procedural Fallback Tree: create-azure-agent

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: create-azure-agent

## 1. Scaffold Script Execution Failure
If the underlying Python scaffold script crashes or throws an exception due to a missing template or filesystem error:
- **Action**: Halt the primary workflow. Read the explicit Python stack trace and correct the syntax error if obvious. Otherwise, output the exact stack trace to the user and prompt them to resolve the missing dependency.

## 2. Illegal Directory Write
If the destination path specifically requested by the user does not exist or lacks write permissions:
- **Action**: Stop execution. Do not attempt to guess an alternative path. Prompt the user with a list of available directories and ask them to choose or create the target path manually.

## 3. Template Rendering Engine Crash
If Jinja2 or the internal string templater fails to render constraints due to malformed input during generation:
- **Action**: Do not output partially-rendered code logic. Fallback to extracting the literal variables given by the user, provide the base template inline in the chat, and instruct the user to insert the values manually.

## 4. Name Collision
If the user requests a generation that shares a name with an already existing skill or plugin in the exact same path:
- **Action**: Do NOT overwrite the existing directory without an explicit dual-confirmation loop. Ask the user: "Warning: Directory already exists. Do you want to recursively overwrite it? (yes/no)".


## See Also

- [[procedural-fallback-tree-create-sub-agent]]
- [[procedural-fallback-tree-create-sub-agent]]
- [[procedural-fallback-tree-create-sub-agent]]
- [[procedural-fallback-tree-agent-swarm]]
- [[procedural-fallback-tree-create-agentic-workflow]]
- [[procedural-fallback-tree-create-command]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-azure-agent/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:09.777848+00:00
