---
concept: procedural-fallback-tree-gemini-cli-agent
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/gemini-cli-agent/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.094204+00:00
cluster: model
content_hash: a7c27f12e97c0c4b
---

# Procedural Fallback Tree: Gemini CLI Agent

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Gemini CLI Agent

## 1. gemini Command Not Found
If `gemini` is not on PATH:
- **Action**: Report the missing CLI. Provide install instructions (npm install -g @google/gemini-cli or equivalent). Do NOT simulate Gemini behavior inline.

## 2. Model Not Available (-m flag error)
If the specified model with `-m` is not available or returns a model-not-found error:
- **Action**: Report the failed model name. Fall back to the default model only with user confirmation. Do NOT silently use a different model without disclosure.

## 3. File Too Large for Pipe
If the CLI blocks on a massive file:
- **Action**: Build a Python chunking script to semantically split the content. Never force the full file through a single pipe invocation.

## 4. Session Not Authenticated
If the CLI fails with an authentication or quota error:
- **Action**: Report the authentication failure. Instruct the user to re-authenticate via the Gemini CLI login flow. Do NOT retry silently.


## See Also

- [[procedural-fallback-tree-claude-cli-agent]]
- [[procedural-fallback-tree-copilot-cli-agent]]
- [[procedural-fallback-tree-claude-cli-agent]]
- [[procedural-fallback-tree-claude-cli-agent]]
- [[procedural-fallback-tree-copilot-cli-agent]]
- [[procedural-fallback-tree-copilot-cli-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/gemini-cli-agent/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.094204+00:00
