---
concept: agent-agentic-os-hooks
source: plugin-code
source_file: spec-kitty-plugin/.agents/hooks/agent-agentic-os-hooks.json
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.053252+00:00
cluster: command
content_hash: 923bcc15e755259c
---

# Agent Agentic Os Hooks

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/session_start.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/update_memory.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/post_run_metrics.py"
          }
        ]
      }
    ]
  }
}


## See Also

- [[agent-loops-hooks]]
- [[agentic-os-guide]]
- [[agentic-os-operational-guide-usage]]
- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[after-os-evolution-verifier-run]]
- [[agent-bridge]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/hooks/agent-agentic-os-hooks.json`
- **Indexed:** 2026-04-27T05:21:04.053252+00:00
