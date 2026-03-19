# Backlog: Embedding-based skill routing

**Plugin**: agent-agentic-os
**Priority**: Low
**Source**: gpt5-critical-review.md - Issue #6 (Keyword-based routing is brittle)
**Target version**: 2.0.0

## Problem

`eval_runner.py` uses keyword overlap between prompts and skill frontmatter to simulate
routing. This is a heuristic proxy:
- Easy to game (add keywords to description, score improves without real improvement)
- Does not generalize to paraphrases the description didn't anticipate
- Cosine similarity over embeddings would materially outperform keyword overlap

## Proposed Solution

### Phase A: cosine similarity baseline (no external deps)
Use Python's `math` + `collections` to implement TF-IDF cosine similarity over the
skill's full frontmatter description vs. the eval prompts. No new dependencies.

```python
def cosine_similarity(text_a: str, text_b: str) -> float:
    # TF-IDF vectors over word tokens, dot product / (|a| * |b|)
    ...
```

Replace `len(overlap) > 0` with `cosine_similarity(...) > 0.15` threshold.
Record as `tfidf_routing_score` in `results.tsv` alongside existing `accuracy`.

### Phase B: embedding-based routing (optional, requires Ollama or API)
If `SKILL_ROUTER_BACKEND=ollama` env var is set, call Ollama's embedding endpoint
(`nomic-embed-text` model) to get real semantic embeddings.
Write the score to the existing `llm_routing_score` column in `results.tsv`.

```python
# eval_runner.py --skill path/to/SKILL.md --backend ollama
```

## Migration Impact

- `eval_runner.py` gains `--backend keyword|tfidf|ollama` flag (default: keyword)
- `results.tsv` gains `tfidf_routing_score` column
- `llm_routing_score` column already exists (added in v1.2.0), gets populated by Phase B
- `skill-improvement-eval/SKILL.md` scope caveat updated to reference the new options

## Acceptance Criteria

- [ ] TF-IDF scorer outperforms keyword overlap on existing evals (measured)
- [ ] Ollama backend is optional and gracefully skipped if not available
- [ ] `results.tsv` records which backend was used
- [ ] No regression on existing keyword baseline behavior
