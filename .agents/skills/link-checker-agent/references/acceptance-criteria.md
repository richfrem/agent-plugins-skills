# Acceptance Criteria: Link Checker

The link-checker skill must meet the following criteria to be considered operational:

## 1. File Inventory (Step 1)
- [ ] `scripts/01_build_file_inventory.py` correctly indexes all `.md` and source files within the target repository.
- [ ] The generated `file_inventory.json` maps basenames to relative paths and ignores blocked directories (`.git`, `node_modules`, `.venv`, etc.).

## 2. Link Extraction (Step 2)
- [ ] `scripts/02_extract_link_references.py` correctly extracts all relative `[text](path)` and `![alt](path)` references from `.md` and source files.
- [ ] The generated `link_references.json` maps each source file to its list of references with line numbers and types.
- [ ] Pipeline output files (`broken_links.json`, `unfixable_links_report.md`, etc.) are excluded from scanning on re-runs.

## 3. Audit (Step 3)
- [ ] `scripts/03_audit_broken_links.py` correctly identifies references whose resolved path does not exist on the filesystem.
- [ ] Outputs both `broken_links.log` (human-readable) and `broken_links.json` (machine-readable with candidates).

## 4. Auto-Fix (Step 4)
- [ ] `scripts/04_autofix_unique_links.py` reads `broken_links.json` to target only affected files (not a full repo walk).
- [ ] Correctly fixes both standard links `[label](path)` and image links `![alt](path)`.
- [ ] Only rewrites links with a **unique** basename match in the inventory; skips ambiguous and missing entries.
- [ ] `--dry-run` prints proposed changes without modifying any files and does NOT write `remaining_broken_links.json`.
- [ ] `--backup` creates `.bak` copies before modifying files.
- [ ] After a real (non-dry-run) fix, writes `remaining_broken_links.json` containing only items that are still broken after fixes were applied.

## 5. Report (Step 5)
- [ ] `scripts/05_report_unfixable_links.py` generates `unfixable_links_report.md` grouping remaining broken links by source file.
- [ ] Report distinguishes `MISSING` (no candidates) from `AMBIGUOUS` (multiple candidates).
- [ ] When `remaining_broken_links.json` exists (written by Step 4), Step 5 uses it as input — not the raw `broken_links.json` — so fixed links do not appear in the report.
- [ ] Reports "No broken links found" when the input file is empty (all issues resolved).
