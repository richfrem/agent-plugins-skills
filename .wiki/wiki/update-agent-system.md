---
concept: update-agent-system
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/plugin-manager_update.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.323473+00:00
cluster: plugin-code
content_hash: b343e7416e09094e
---

# Update Agent System

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: >-
  Run the full agent system update: refresh all plugin code and redeploy
  capabilities to all agent environments.
args:
  dry_run:
    description: "Preview what would change without modifying files."
    type: boolean
---

# Update Agent System

Runs the master sync to update all plugins and redeploy capabilities to all agent environments.

```bash
if [ "${dry_run}" = "true" ]; then
    python ././scripts/plugin_add.py --all -y --dry-run
else
    python ././scripts/plugin_add.py --all -y
fi
```

> For full control over each step, invoke the `plugin-maintenance` skill.


## See Also

- [[agent-harness-learning-layer-formerly-agentic-os]]
- [[agent-harness-summary]]
- [[os-health-check-sub-agent]]
- [[global-agent-kernel]]
- [[triple-loop-learning-system---architecture-overview]]
- [[template-post-run-agent-self-assessment]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/plugin-manager_update.md`
- **Indexed:** 2026-04-17T06:42:10.323473+00:00
