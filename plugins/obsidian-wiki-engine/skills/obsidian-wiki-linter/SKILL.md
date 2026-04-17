---
name: obsidian-wiki-linter
description: "Runs a semantic health check over the Obsidian LLM wiki using the cheapest available LLM CLI. Finds inconsistencies, missing concepts, stale articles, connection candidates, and new article suggestions. Writes a structured report to meta/lint-report.md. Use when the wiki is large enough to have quality drift, or as a periodic maintenance step."
allowed-tools: Bash, Read, Write
---

## Dependencies

Requires Python 3.8+ and at least one CLI installed: `copilot`, `claude`, or `gemini`.

```bash
pip install -r requirements.txt
```

---
# Obsidian Wiki Linter

**Status:** Active
**Author:** Richard Fremmerlid
**Domain:** Obsidian Wiki Engine

## Purpose

Performs a semantic health check over the LLM wiki — the step Karpathy calls
"linting." Unlike `audit.py` (which checks structural coverage: orphans, missing
summaries, broken wikilinks), this skill uses an LLM to analyze *semantic quality*:
contradictions, knowledge gaps, and connection opportunities that only emerge once
the wiki is large enough to have internal consistency requirements.

## What It Checks

| Category | What it finds |
|:---------|:--------------|
| **Inconsistencies** | Contradicting claims between two concept pages |
| **Missing Concepts** | Topics implied by existing articles but not yet written |
| **Stale Articles** | Pages with vague, outdated, or thin content |
| **Connection Candidates** | Concept pairs that should have wikilinks but don't |
| **New Article Suggestions** | Topics the wiki should cover based on its current scope |

## Usage

### Run semantic health check (default engine)
```bash
python ./scripts/lint_wiki.py --wiki-root /path/to/wiki-root
```

### Sample more pages for larger wikis
```bash
python ./scripts/lint_wiki.py --wiki-root /path/to/wiki-root --sample 30
```

### Force engine
```bash
python ./scripts/lint_wiki.py --wiki-root /path/to/wiki-root --engine claude
```

### Dry run (print prompt without calling LLM)
```bash
python ./scripts/lint_wiki.py --wiki-root /path/to/wiki-root --dry-run
```

## Engine Fallback Chain

Same strict cheap-model chain as `obsidian-rlm-distiller`:
```
1. copilot  → gpt-5-mini        (free with Copilot Pro)
2. claude   → claude-haiku-4-5  (fallback)
3. gemini   → gemini-3-flash-preview (final fallback)
```

## Output

Report is written to `{wiki-root}/meta/lint-report.md` with YAML frontmatter:
```yaml
generated_at: "2026-04-16T..."
engine: "claude"
model: "claude-haiku-4-5"
```

Followed by five sections:
1. **Inconsistencies** — conflicting claims between articles
2. **Missing Concepts** — implied but not yet written
3. **Stale or Weak Articles** — need richer content
4. **Connection Candidates** — wikilinks to add
5. **New Article Suggestions** — fresh topics to write

## When to Use

- After the wiki reaches ~20+ concept nodes (semantic quality starts to matter)
- As a weekly maintenance step before a major query session
- When you notice the wiki feels inconsistent or fragmented
- Before filing `--save-as` outputs back — lint first to know what gaps to fill
- As the final step in `/wiki-rebuild` (after ingest, distill, build)

## Audit vs. Lint

| `audit.py` | `lint_wiki.py` |
|:-----------|:---------------|
| Structural: missing summaries, broken links, orphans | Semantic: contradictions, gaps, stale content |
| Always fast, no LLM needed | Requires LLM call |
| Run before every `/wiki-query` | Run periodically (weekly or post-rebuild) |
| Exit code 1 on critical issues | Always exits 0 (report-only) |

## Related Scripts

- `lint_wiki.py` — semantic health check orchestrator
- `audit.py` — structural coverage checker (complementary)
- `distill_wiki.py` — shares engine detection logic
