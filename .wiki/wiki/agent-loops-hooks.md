---
concept: agent-loops-hooks
source: plugin-code
source_file: spec-kitty-plugin/.agents/hooks/agent-loops-hooks.json
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.053377+00:00
cluster: exit
content_hash: 7a2e08639e0cea68
---

# Agent Loops Hooks

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

{
    "hooks": [
        {
            "type": "Stop",
            "description": "Prevents premature session exit without completing the closure sequence (Seal, Persist, Retrospective). Checks for an active loop state file and blocks exit if closure phases are incomplete.",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/closure_guard.py"
        }
    ]
}


## See Also

- [[agent-agentic-os-hooks]]
- [[agent-loops-execution-primitives]]
- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[agent-bridge]]
- [[agent-harness-learning-layer]]
- [[agent-scaffolders-spec-factory]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/hooks/agent-loops-hooks.json`
- **Indexed:** 2026-04-27T05:21:04.053377+00:00
