---
concept: rlm-audit
source: plugin-code
source_file: rlm-factory/skills/rlm-audit/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.676306+00:00
cluster: cache
content_hash: 69b683ed7537b9e2
---

# rlm-audit

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# rlm-audit
---
name: rlm-audit
description: Audit RLM cache coverage - compare manifest against filesystem
trigger_phrases:
  - "audit rlm cache"
  - "check rlm coverage"
  - "rlm inventory audit"
  - "show missing rlm files"
  - "check rlm gap"
---

## Purpose
Systematically audit the RLM (Recursive Language Model) semantic cache to identify gaps between the project manifest and the actual summary files stored on disk. 

## Capabilities
- **Coverage Analysis**: Calculates the percentage of project documentation currently summarized.
- **Gap Identification**: Detects files that are included in the manifest but missing from the cache.
- **Exporting**: Generates CSV lists of missing files for batch processing.
- **Validation**: Ensures the cache directory structure mirrors the source repository.

## Usage
Run the audit for a specific profile to see what's missing:

`ash
python scripts/audit_cache.py --profile wiki --report audit_report.txt --csv missing_files.csv
`

## Related
- **rlm-distill-agent**: Use to fill the gaps identified by this audit.
- **rlm-cleanup-agent**: Use to remove stale entries from the cache.


## See Also

- [[audit-rlm-inventory]]
- [[audit-rlm-inventory]]
- [[audit-rlm-inventory]]
- [[red-team-audit-template-epistemic-integrity-check]]
- [[self-audit-analyze-the-analyzer]]
- [[pattern-artifact-embedded-execution-audit-trail]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `rlm-factory/skills/rlm-audit/SKILL.md`
- **Indexed:** 2026-04-17T06:42:09.676306+00:00
