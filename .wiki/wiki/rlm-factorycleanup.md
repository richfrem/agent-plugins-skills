---
concept: rlm-factorycleanup
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/rlm-factory_cleanup.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.323784+00:00
cluster: remove
content_hash: dbc9e97e61a434ff
---

# /rlm-factory:cleanup

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: Remove stale and orphaned entries from the RLM Summary Ledger (offline)
argument-hint: "[--profile project|tools] [--apply]"
---

# /rlm-factory:cleanup

Remove stale entries (deleted files) and orphans (files outside manifest scope) from the ledger.

> **For detailed execution protocol, see agent:** `rlm-cleanup`

## Quick Reference

```bash
# Dry run -- see what would be removed (safe, no changes)
python3 ./scripts/cleanup_cache.py --profile project

# Apply -- actually remove stale entries
python3 ./scripts/cleanup_cache.py --profile project --apply

# Both profiles
python3 ./scripts/cleanup_cache.py --profile tools --apply
```

**Dry run by default.** Nothing is deleted without `--apply`.


## See Also

- [[obsidian-rlm-distiller]]
- [[rlm-factory-plugin]]
- [[rlm-core-philosophy-summarize-once-reuse-many]]
- [[rlm-core-philosophy-summarize-once-reuse-many]]
- [[audit-rlm-inventory]]
- [[rlm-factorydistill]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/rlm-factory_cleanup.md`
- **Indexed:** 2026-04-17T06:42:10.323784+00:00
