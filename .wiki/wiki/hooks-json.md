---
concept: hooks-json
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-init/assets/templates/HOOKS_JSON.json
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.290367+00:00
cluster: command
content_hash: 3bbe740ee92ffaec
---

# Hooks Json

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/os-init/assets/templates/HOOKS_JSON.json -->
{
  "hooks": {
    "SessionStart": [
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


<!-- Source: plugin-code/agent-agentic-os/assets/templates/HOOKS_JSON.json -->
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python${CLAUDE_PLUGIN_ROOT}/hooks/update_memory.py"
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
            "command": "python${CLAUDE_PLUGIN_ROOT}/hooks/update_memory.py"
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
            "command": "python${CLAUDE_PLUGIN_ROOT}/hooks/scripts/post_run_metrics.py"
          }
        ]
      }
    ]
  }
}

## See Also

- [[agent-agentic-os-hooks]]
- [[agent-loops-hooks]]
- [[exploration-cycle-plugin-hooks]]
- [[fix-1-literal-n-chars-write-back-immediately-so-json-parse-can-proceed]]
- [[hooks]]
- [[initialize-empty-hooks-schema-in-a-nested-hooks-dir]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-init/assets/templates/HOOKS_JSON.json`
- **Indexed:** 2026-04-27T05:21:04.290367+00:00
