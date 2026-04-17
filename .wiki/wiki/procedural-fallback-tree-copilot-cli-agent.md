---
concept: procedural-fallback-tree-copilot-cli-agent
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/copilot-cli-agent/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.754345+00:00
cluster: action
content_hash: 9401d4e1ba2ee887
---

# Procedural Fallback Tree: Copilot CLI Agent

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Copilot CLI Agent

## 1. copilot Command Not Found
If `copilot` is not on PATH:
- **Action**: Report the missing CLI. Provide install instructions (gh extension install github/gh-copilot or equivalent). Do NOT simulate Copilot behavior inline.

## 2. Smoke Test Fails
If 'copilot -p "Reply with exactly: COPILOT_CLI_OK"' does not return the expected string:
- **Action**: HALT. Do NOT dispatch the full analysis task. Report the smoke test failure. Ask user to verify CLI installation, PATH, and authentication before retrying.

## 3. Permission Flag Required by Task
If a task appears to require elevated permission flags (--allow-all-tools, --allow-all-paths):
- **Action**: Ask the user to confirm whether the elevated access is intentional. Document the reason in the command. Default is always to run without elevated permissions.

## 4. Session Not Authenticated
If the CLI returns an authentication error:
- **Action**: Report the failure and instruct the user to authenticate via the Copilot CLI session interactively. Do NOT retry in a background process.


## See Also

- [[procedural-fallback-tree-claude-cli-agent]]
- [[procedural-fallback-tree-gemini-cli-agent]]
- [[procedural-fallback-tree-claude-cli-agent]]
- [[procedural-fallback-tree-claude-cli-agent]]
- [[procedural-fallback-tree-gemini-cli-agent]]
- [[procedural-fallback-tree-gemini-cli-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/copilot-cli-agent/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:09.754345+00:00
