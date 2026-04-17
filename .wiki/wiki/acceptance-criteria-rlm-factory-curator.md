---
concept: acceptance-criteria-rlm-factory-curator
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/rlm-curator/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.199477+00:00
cluster: must
content_hash: c6a1aef38fbc565f
---

# Acceptance Criteria: RLM Factory (Curator)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: RLM Factory (Curator)

The `rlm-factory` workflow MUST satisfy the following success metrics:

1. **Strict Electric Fence Adherence (Concurrent Integrity)**: During distillation or updates, the agent MUST NEVER be caught executing raw text insertion (via OS commands or core IDE blocks) directly into the `rlm_summary_cache.json` file. It must always tunnel through `inject_summary.py` or semantic tools to respect file-locking patterns (`fcntl.flock`).
2. **Deterministic Backoff**: If the agent attempts an Ollama distillation but the local engine is off, it must mathematically identify the refusal and gracefully exit or fallback according to the `fallback-tree.md` without polluting the context with false retry attempts.


## See Also

- [[acceptance-criteria-rlm-init]]
- [[acceptance-criteria-rlm-init]]
- [[acceptance-criteria-rlm-init]]
- [[acceptance-criteria-adr-manager]]
- [[acceptance-criteria-os-clean-locks]]
- [[acceptance-criteria-os-clean-locks]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/rlm-curator/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.199477+00:00
