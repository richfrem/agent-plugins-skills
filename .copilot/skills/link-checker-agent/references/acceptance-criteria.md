# Acceptance Criteria: Link Checker

The link-checker skill must meet the following criteria to be considered operational:

## 1. File Inventory Mapping
- [ ] The `map_repository_files.py` script correctly indexes all `.md` files within the target repository.
- [ ] The generated `file_inventory.json` ignores blocked directories like node_modules or .venv.

## 2. Smart Fix Resolution
- [ ] The `smart_fix_links.py` script correctly identifies broken `[text](broken-link)` patterns in target files.
- [ ] The script accurately resolves unambiguous basename matches using the inventory index and updates the markdown to the correct relative path.

## 3. Audit Logging
- [ ] The `check_broken_paths.py` script identifies remaining invalid documentation links.
- [ ] It outputs a comprehensive `broken_links.log` indicating unresolvable or missing anchor segments.
