---
concept: audit-rlm-inventory
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/rlm-factory_audit.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.323630+00:00
cluster: cache
content_hash: 5f52eabe606e6d7c
---

# Audit RLM Inventory

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: Audit RLM cache coverage — compare ledger against filesystem (offline)
argument-hint: "[--type legacy|tool]"
---

# Audit RLM Inventory

Compare the ledger against the actual filesystem to report coverage gaps.

## Usage
```bash
# Audit legacy docs coverage
python ./scripts/inventory.py --profile project

# Audit tool scripts coverage
python ./scripts/inventory.py --profile tools
```

## Output
- Files on disk vs entries in cache
- Coverage percentage
- Missing files (not yet distilled)
- Stale entries (files deleted but still in cache)


## See Also

- [[rlm-audit]]
- [[red-team-audit-template-epistemic-integrity-check]]
- [[self-audit-analyze-the-analyzer]]
- [[pattern-artifact-embedded-execution-audit-trail]]
- [[portability-audit-report]]
- [[acceptance-criteria-audit-plugin]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/rlm-factory_audit.md`
- **Indexed:** 2026-04-17T06:42:10.323630+00:00
