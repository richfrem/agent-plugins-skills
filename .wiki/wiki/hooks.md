---
concept: hooks
source: plugin-code
source_file: agent-agentic-os/hooks/hooks.json
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.975169+00:00
cluster: command
content_hash: b521c31df95da585
---

# Hooks

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-agentic-os/hooks/hooks.json -->
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python ${CLAUDE_PLUGIN_ROOT}/hooks/session_start.py"
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
            "command": "python ${CLAUDE_PLUGIN_ROOT}/hooks/update_memory.py"
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
            "command": "python ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/post_run_metrics.py"
          }
        ]
      }
    ]
  }
}

<!-- Source: plugin-code/exploration-cycle-plugin/hooks/hooks.json -->
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python ${CLAUDE_PLUGIN_ROOT}/hooks/session_start.py"
          }
        ]
      }
    ],
    "SessionStop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python ${CLAUDE_PLUGIN_ROOT}/hooks/session_end.py"
          }
        ]
      }
    ]
  }
}


<!-- Source: plugin-code/agent-loops/hooks/hooks.json -->
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python ${CLAUDE_PLUGIN_ROOT}/scripts/closure_guard.py",
            "description": "Prevents premature session exit without completing the closure sequence (Seal, Persist, Retrospective). Checks for an active loop state file and blocks exit if closure phases are incomplete."
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
- [[hooks-json]]
- [[initialize-empty-hooks-schema-in-a-nested-hooks-dir]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/hooks/hooks.json`
- **Indexed:** 2026-04-27T05:21:03.975169+00:00
