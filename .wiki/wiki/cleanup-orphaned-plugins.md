---
concept: cleanup-orphaned-plugins
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/plugin-manager_cleanup.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.323118+00:00
cluster: artifacts
content_hash: fa395f2b6c8b1972
---

# Cleanup Orphaned Plugins

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: >
  Clean up orphaned artifacts left behind by plugins that have been removed
  from the local plugins/ directory.
args:
  dry_run:
    description: "Preview what would be deleted without making changes."
    type: boolean
---

# Cleanup Orphaned Plugins

Identifies plugins removed from `plugins/` that still have lingering artifacts (skills, rules, workflows) in agent directories, and safely removes them.

> **Safety**: Only deletes artifacts for vendor-originated plugins. Project-specific custom plugins are never touched.

```bash
echo "Running orphan cleanup analysis..."

if [ "${dry_run}" = "true" ]; then
    python3 ././scripts/clean_orphans.py --dry-run
else
    python3 ././scripts/clean_orphans.py
fi
```

> For a full sync (install new + cleanup removed), use the `/plugin-manager:update` command.


## See Also

- [[mine-plugins]]
- [[adr-004-self-contained-plugins---no-cross-plugin-script-dependencies]]
- [[adr-004-self-contained-plugins---no-cross-plugin-script-dependencies]]
- [[mine-plugins]]
- [[adr-004-self-contained-plugins---no-cross-plugin-script-dependencies]]
- [[plugins-research]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/plugin-manager_cleanup.md`
- **Indexed:** 2026-04-17T06:42:10.323118+00:00
