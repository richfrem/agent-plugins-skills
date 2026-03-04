# Acceptance Criteria: RLM Factory (Curator)

The `rlm-factory` workflow MUST satisfy the following success metrics:

1. **Strict Electric Fence Adherence (Concurrent Integrity)**: During distillation or updates, the agent MUST NEVER be caught executing raw text insertion (via OS commands or core IDE blocks) directly into the `rlm_summary_cache.json` file. It must always tunnel through `inject_summary.py` or semantic tools to respect file-locking patterns (`fcntl.flock`).
2. **Deterministic Backoff**: If the agent attempts an Ollama distillation but the local engine is off, it must mathematically identify the refusal and gracefully exit or fallback according to the `fallback-tree.md` without polluting the context with false retry attempts.
