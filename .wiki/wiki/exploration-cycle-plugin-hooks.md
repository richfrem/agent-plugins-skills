---
concept: exploration-cycle-plugin-hooks
source: plugin-code
source_file: spec-kitty-plugin/.agents/hooks/exploration-cycle-plugin-hooks.json
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.053487+00:00
cluster: sessionstart
content_hash: 101512d58e10091e
---

# Exploration Cycle Plugin Hooks

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

{
  "SessionStart": {
    "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/session_start.py"
  }
}

## See Also

- [[domain-patterns-exploration-cycle]]
- [[add-script-dir-to-path-to-import-plugin-inventory]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[adr-004-self-contained-plugins---no-cross-plugin-script-dependencies]]
- [[agent-agentic-os-hooks]]
- [[agent-loops-hooks]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/hooks/exploration-cycle-plugin-hooks.json`
- **Indexed:** 2026-04-27T05:21:04.053487+00:00
