# Acceptance Criteria: Vector DB Agent

This skill MUST satisfy the following success metrics:

1. **Strict Electric Fence Adherence (Database Sovereignty)**: During queries or ingestion, the agent MUST NEVER be caught executing raw text retrieval (via `cat`, `grep`, `sqlite3`) directly against the underlying `.vector_data` storage binaries. It must always tunnel through `scripts/query.py`.
2. **Transparent Failure States**: If an embedded query yields zero results from the parent-child node maps, the agent mathematically implements the **Source Transparency Declaration**, proving identically what it searched and what scope was missing from its retrieval window, rather than hallucinating generic advice.
