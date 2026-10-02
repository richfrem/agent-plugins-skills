---
name: symlink-manager
plugin: dev-utils
description: >
  Create, audit, repair, and document cross-platform symlinks. Use when the user
  mentions symlinks, junctions, broken links after git pull, cross-platform path
  issues, or missing files after switching machines. Supports macOS/Linux and
  Windows; Windows users need Developer Mode or administrator rights before
  creating true symlinks.
allowed-tools: Bash, Read, Write
---

# Symlink Manager (`symlink-manager`)

Create, audit, repair, and document cross-platform symlinks across macOS, Linux, and Windows.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Real Symlinks Only**: Never substitute hardlinks or plain text files for Git symlinks.
2. **No Symlink Chaining**: Target must be a regular file or directory, never another symlink.
3. **Hub-and-Spoke Invariant**: Canonical assets live at plugin root (`scripts/`, `references/`, `assets/`); spokes link directly to hub.
4. **Register in Manifest**: All created symlinks must be recorded in `symlinks.json`.
5. **Windows Support**: Developer Mode (or admin elevation) required for unprivileged symlink creation (`git config core.symlinks true`).

## Quick start

Diagnose environment, Git settings, and existing symlink health:

```bash
python3 scripts/symlink_manager.py diagnose
```

## Workflow

1. **Step 1 (Diagnose)**: Run `python3 scripts/symlink_manager.py diagnose` to check Git configuration and link health.
2. **Step 2 (Configure)**: On Windows, enable Developer Mode and run `git config core.symlinks true`. On macOS/Linux, verify `core.symlinks` is true.
3. **Step 3 (Create/Restore)**:
   - Create single link: `python3 scripts/symlink_manager.py create --src <hub-path> --dst <spoke-path>`
   - Restore all manifest links: `python3 scripts/symlink_manager.py restore`
4. **Step 4 (Bulk Repair)**: Recursively scan and repair text-file stand-ins with `python3 scripts/bulk_symlink_fixer.py <target-directory>`.

## Verification

Audit repository symlink health and integrity against `symlinks.json`:

```bash
python3 scripts/symlink_manager.py audit
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria and validation gates.
- [troubleshooting.md](references/troubleshooting.md) — Troubleshooting for Windows permissions, CI configuration, and APFS issues.
