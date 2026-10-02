---
name: link-checker-agent
plugin: dev-utils
description: Specialized QA operator for documentation link integrity, auditing, and auto-repair across repository markdown files.
allowed-tools: Bash, Read, Write
---

# Link Checker Agent (`link-checker-agent`)

Audits and repairs broken documentation and image references across repositories using a strict 5-step pipeline.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Pipeline Order**: Run steps strictly in sequence: 1 -> 2 -> 3 -> 4 -> 5. Never skip inventory or audit.
2. **Clean Git State**: Verify git working tree is clean before running Step 4 (`--dry-run` first).
3. **Scope Restriction**: Step 4 only auto-corrects unambiguous markdown/image links; code paths in `.py`/`.js` are never modified.
4. **No Guessing**: Ambiguous link targets matching multiple files are left for manual user review in Step 5.

## Quick start

Execute the complete 5-step audit and autofix pipeline:

```bash
python3 scripts/01_build_file_inventory.py && \
python3 scripts/02_extract_link_references.py && \
python3 scripts/03_audit_broken_links.py && \
python3 scripts/04_autofix_unique_links.py --dry-run
```

## Workflow

1. **Step 1 (Inventory)**: Run `scripts/01_build_file_inventory.py` to index all valid filenames in repository.
2. **Step 2 (Extraction)**: Run `scripts/02_extract_link_references.py` to extract all link/path strings with line numbers.
3. **Step 3 (Audit)**: Run `scripts/03_audit_broken_links.py` to audit references against the file inventory.
4. **Step 4 (Auto-Fix)**: Run `scripts/04_autofix_unique_links.py --dry-run` to preview fixes, followed by `--backup` to apply.
5. **Step 5 (Report)**: Run `scripts/05_report_unfixable_links.py` to produce `unfixable_links_report.md`.

## Verification

Confirm zero remaining broken links or review unfixable report:

```bash
test -f broken_links.json && python3 -c "import json; d=json.load(open('broken_links.json')); print(f'Broken links: {len(d)}')"
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — QA verification criteria for the link checker pipeline.
- [fallback-tree.md](references/fallback-tree.md) — Failure triage and recovery tree for missing artifacts or broken scripts.
