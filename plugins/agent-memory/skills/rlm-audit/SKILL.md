---
name: rlm-audit
plugin: agent-memory
description: Audit RLM cache coverage - compare manifest against filesystem
trigger_phrases:
  - "audit rlm cache"
  - "check rlm coverage"
  - "rlm inventory audit"
  - "show missing rlm files"
  - "check rlm gap"
---

# RLM Cache Audit (`rlm-audit`)

Systematically audit the RLM (Recursive Language Model) semantic cache to identify coverage gaps between the project manifest and distilled summary files stored on disk.

## Contents

- [Critical Constraints](#critical-constraints)
- [Capabilities](#capabilities)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)

## Critical Constraints

1. **Read-Only Operation**: The audit script only reads files and emits reports; it never modifies the cache or manifest.
2. **Profile Specification**: Always specify `--profile` to ensure the correct manifest and directory mappings are evaluated.
3. **Standard Library**: Audit operations rely on standard Python with zero external vector or database dependencies.

## Capabilities

- **Coverage Analysis**: Calculates the percentage of project documentation currently summarized.
- **Gap Identification**: Detects files included in the manifest but missing from the cache.
- **Batch Exporting**: Generates CSV lists of missing files for distillation pipelines.
- **Structure Validation**: Verifies that the cache directory structure mirrors the source repository.

## Quick start

Run the audit for a specified profile to inspect cache coverage:

```bash
python3 scripts/audit_cache.py --profile wiki --report audit_report.txt --csv missing_files.csv
```

## Workflow

1. **Identify Profile**: Determine target documentation or code profile (`wiki`, `repo`, etc.).
2. **Execute Audit**: Run `audit_cache.py` comparing the active manifest against cached summary artifacts.
3. **Analyze Gaps**: Review `audit_report.txt` for missing document summaries and percentage coverage.
4. **Export Worklist**: Export `missing_files.csv` to supply target queues for `rlm-distill-agent`.

## Verification

Confirm report and CSV generation with valid non-empty summary metrics:

```bash
python3 scripts/audit_cache.py --profile wiki --check-only
```
