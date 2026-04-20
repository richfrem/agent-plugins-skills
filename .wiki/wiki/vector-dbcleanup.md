---
concept: vector-dbcleanup
source: plugin-code
source_file: vector-db/commands/cleanup.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.423774+00:00
cluster: deleted
content_hash: 5fd422d5657e95f8
---

# /vector-db:cleanup

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: Remove stale chunks from deleted or renamed files in the vector database
---

# /vector-db:cleanup

Remove orphaned chunks from the vector store for files that no longer exist on disk.

> **For detailed execution protocol, see agent:** `vector-db-cleanup`

## Quick Reference

```bash
# Dry run -- see what would be removed
python ./scripts/cleanup.py --profile wiki--dry-run

# Apply
python ./scripts/cleanup.py --profile wiki--apply
```

**Dry run by default.** Nothing is deleted without `--apply`.
Prevents deleted files from returning false positives in semantic search.


## See Also

- [[vector-consistency-stabilizer]]
- [[code-file-vector-consistency-checkpy]]
- [[vector-consistency-stabilizer]]
- [[code-file-vector-consistency-checkpy]]
- [[vector-db-initialization]]
- [[acceptance-criteria-vector-db-init]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `vector-db/commands/cleanup.md`
- **Indexed:** 2026-04-17T06:42:10.423774+00:00
