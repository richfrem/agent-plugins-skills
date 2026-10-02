# Obsidian Wiki Semantic Linting Guide

## Contents
- [Semantic Check Categories](#semantic-check-categories)
- [Report Format & Output Schema](#report-format--output-schema)
- [Structural Audit vs Semantic Linting](#structural-audit-vs-semantic-linting)
- [Engine Execution Matrix](#engine-execution-matrix)

---

## Semantic Check Categories

| Category | Diagnostic Scope |
|:---------|:-----------------|
| **Inconsistencies** | Contradictory statements or facts across different concept nodes |
| **Missing Concepts** | Implied or referenced topics lacking dedicated concept pages |
| **Stale / Thin Content** | Nodes with vague, incomplete, or outdated information |
| **Connection Candidates** | Concept pairs with strong semantic ties lacking bidirectional wikilinks |
| **New Topic Proposals** | Emergent subject areas suggested by repository evolution |

---

## Report Format & Output Schema

Reports land at `{wiki_root}/meta/lint-report.md` with structured metadata:

```yaml
---
generated_at: "2026-10-02T12:00:00Z"
engine: "copilot"
model: "gpt-5-mini"
sampled_nodes: 25
---
```

Followed by actionable remediation sections:
1. `## Inconsistencies`
2. `## Missing Concepts`
3. `## Stale Articles`
4. `## Connection Candidates`
5. `## Proposed Articles`

---

## Structural Audit vs Semantic Linting

| Dimension | `audit.py` (Structural) | `lint_wiki.py` (Semantic) |
|:----------|:------------------------|:--------------------------|
| **Focus** | Missing files, orphans, broken wikilinks | Contradictions, semantic gaps, weak text |
| **Engine** | Pure Python (no LLM, 0 cost) | Cheap LLM CLI (`gpt-5-mini`, `claude-haiku-4-5`) |
| **Frequency** | Pre-commit / pre-query | Periodic maintenance (weekly / post-rebuild) |
| **Exit Code** | Non-zero on broken invariants | Always exits 0 (report generation) |

---

## Engine Execution Matrix

```bash
# Default cheap CLI selection
python ./scripts/lint_wiki.py --wiki-root <path>

# Custom sample size
python ./scripts/lint_wiki.py --wiki-root <path> --sample 30

# Explicit backend selection
python ./scripts/lint_wiki.py --wiki-root <path> --engine copilot
python ./scripts/lint_wiki.py --wiki-root <path> --engine claude
```
