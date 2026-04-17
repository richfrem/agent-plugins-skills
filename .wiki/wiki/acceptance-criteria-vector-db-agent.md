---
concept: acceptance-criteria-vector-db-agent
source: plugin-code
source_file: vector-db/skills/vector-db-search/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.439283+00:00
cluster: must
content_hash: 0d00f8602238239e
---

# Acceptance Criteria: Vector DB Agent

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: Vector DB Agent

This skill MUST satisfy the following success metrics:

1. **Strict Electric Fence Adherence (Database Sovereignty)**: During queries or ingestion, the agent MUST NEVER be caught executing raw text retrieval (via `cat`, `grep`, `sqlite3`) directly against the underlying `.vector_data` storage binaries. It must always tunnel through `scripts/query.py`.
2. **Transparent Failure States**: If an embedded query yields zero results from the parent-child node maps, the agent mathematically implements the **Source Transparency Declaration**, proving identically what it searched and what scope was missing from its retrieval window, rather than hallucinating generic advice.


## See Also

- [[acceptance-criteria-vector-db-init]]
- [[acceptance-criteria-vector-db-init]]
- [[acceptance-criteria-vector-db-launch]]
- [[acceptance-criteria-vector-db-init]]
- [[acceptance-criteria-vector-db-launch]]
- [[acceptance-criteria-agent-swarm]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `vector-db/skills/vector-db-search/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.439283+00:00
