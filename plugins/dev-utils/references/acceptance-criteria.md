# Acceptance Criteria — Symlink Manager Skill

This document specifies the validation criteria for confirming the correct operation of the `symlink-manager` skill.

## 1. Environment Diagnosis

- [ ] Running `python ./scripts/symlink_manager.py diagnose` completes successfully on all supported platforms (macOS, Windows, Linux).
- [ ] The command output accurately reports the operating system, current Git `core.symlinks` settings, and developer mode status.

## 2. Symlink Creation

- [ ] Running `python ./scripts/symlink_manager.py create --src <src-path> --dst <dst-path>` creates a symbolic link at the destination pointing to the source.
- [ ] On macOS/Linux, it creates a true symbolic link (`is_symlink()` is true).
- [ ] On Windows with Developer Mode enabled, it creates a true symbolic link.
- [ ] On Windows without Developer Mode, it safely falls back to a junction point for directories or a hardlink for files.
- [ ] The generated symlink uses relative paths to ensure repository portability.
- [ ] The created link is added to the `symlinks.json` manifest.

## 3. Restoration from Manifest

- [ ] Running `python ./scripts/symlink_manager.py restore` successfully re-creates all symlinks listed in `symlinks.json`.
- [ ] Re-running the command skips existing valid symlinks without throwing errors.

## 4. Bulk Fixing

- [ ] Running `python ./scripts/bulk_symlink_fixer.py <directory>` successfully scans the directory recursively.
- [ ] It identifies and restores any broken symlinks or plain text file stand-ins back to active links.
