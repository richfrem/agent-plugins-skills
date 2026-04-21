#!/usr/bin/env python
"""
fix_inside_plugin_symlinks.py
=====================================

Purpose:
    Creates local relative symlinks for files that skills reference inside 
    their parent plugin to preserve distribution containment guarantees.

Layer: Investigate / Repair

Usage Examples:
    python scripts/fix_inside_plugin_symlinks.py temp/inventory.json --project . --dry-run
    python scripts/fix_inside_plugin_symlinks.py temp/inventory.json --project . --apply

Supported Object Types:
    Skill file references.

CLI Arguments:
    inventory: Path to inventory.json (Required)
    --project: Project root (default: .)
    --dry-run: Preview changes only (default: True if no action supplied)
    --apply: Apply fixes on disk

Input Files:
    - inventory.json

Output:
    Console logs listing SYMLINKS and UPDATES applied.

Key Functions:
    - InsidePluginSymlinkFixer.load_inventory()
    - InsidePluginSymlinkFixer.get_plugin_root()
    - InsidePluginSymlinkFixer.analyze()
    - InsidePluginSymlinkFixer.propose_fix()
    - InsidePluginSymlinkFixer.apply_fixes()

Script Dependencies:
    - json
    - sys
    - argparse
    - os
    - subprocess
    - platform
    - Path (pathlib)

Consumed by:
    Static auditor repair workflows.
"""

import json
import sys
import argparse
import os
import subprocess
import platform
from pathlib import Path
from collections import defaultdict

class InsidePluginSymlinkFixer:
    def __init__(self, inventory_file: str | Path, project_root: str | Path) -> None:
        self.inventory_file = Path(inventory_file)
        self.project_root = Path(project_root).resolve()
        self.violations = []
        self.fixes = []
        self.skipped = []

    def load_inventory(self) -> dict:
        """Load inventory.json"""
        with open(self.inventory_file, 'r') as f:
            return json.load(f)

    def get_plugin_root(self, file_path: str) -> tuple[Path | None, str | None]:
        """Extract plugin root from path like plugins/adr-manager/skills/adr-management/file.md"""
        parts = Path(file_path).parts
        if 'plugins' in parts:
            idx = parts.index('plugins')
            if idx + 1 < len(parts):
                plugin_name = parts[idx + 1]
                return Path(*parts[:idx+2]), plugin_name
        return None, None

    def analyze(self) -> None:
        """Find all inside-plugin violations"""
        inventory = self.load_inventory()

        for ref_entry in inventory['references']:
            source_file = ref_entry['source_file']
            reference = ref_entry['reference']
            status = ref_entry.get('status', {})

            # Only check files in plugins/*/skills/*
            if 'plugins' not in source_file or ('/skills/' not in source_file and '\\skills\\' not in source_file):
                continue

            plugin_root, plugin_name = self.get_plugin_root(source_file)
            if not plugin_root or not plugin_name:
                continue

            resolved = status.get('resolved_path')
            if not resolved:
                continue

            resolved_path = Path(resolved)
            plugin_path = self.project_root / plugin_root

            # Check if resolved path is inside the plugin
            try:
                resolved_path.relative_to(plugin_path)
                is_inside = True
            except ValueError:
                is_inside = False

            if is_inside:
                source_full = self.project_root / source_file
                source_dir = source_full.parent

                self.violations.append({
                    'source_file': source_file,
                    'source_full': source_full,
                    'source_dir': source_dir,
                    'plugin_root': plugin_path,
                    'plugin_name': plugin_name,
                    'reference': reference,
                    'resolved_path': resolved_path,
                    'resolved_rel_to_plugin': resolved_path.relative_to(plugin_path),
                })

    def propose_fix(self, violation: dict) -> dict | None:
        """Propose a fix for a violation"""
        source_file = violation['source_file']
        source_full = violation['source_full']
        source_dir = violation['source_dir']
        reference = violation['reference']
        resolved_path = violation['resolved_path']
        resolved_rel = violation['resolved_rel_to_plugin']
        plugin_path = violation['plugin_root']

        # Determine symlink name (just the filename, or last part of path)
        ref_path = Path(reference)
        symlink_name = ref_path.name

        # Full path where symlink should be created
        symlink_full_path = source_dir / symlink_name

        # Skip if symlink already exists pointing to the right target
        if symlink_full_path.exists() or symlink_full_path.is_symlink():
            return None

        # Calculate relative path from symlink to target
        # From source_dir to resolved_path
        rel_to_target = Path(os.path.relpath(resolved_path, source_dir))

        # New reference in source file (just the symlink name since it's local)
        new_reference = f"./{symlink_name}"

        return {
            'source_file': source_file,
            'source_full': source_full,
            'old_reference': reference,
            'new_reference': new_reference,
            'symlink_path': symlink_full_path,
            'symlink_target': rel_to_target,
            'symlink_target_abs': resolved_path,
        }

    def apply_fixes(self) -> int:
        """Apply all fixes"""
        # Group by source file to update references
        by_source = defaultdict(list)

        for violation in self.violations:
            fix = self.propose_fix(violation)
            if not fix:
                self.skipped.append(violation)
                continue

            by_source[fix['source_file']].append(fix)
            self.fixes.append(fix)

        if not self.fixes:
            print("[OK] No fixes to apply")
            return 0

        created_symlinks = set()
        updated_files = set()

        # Create symlinks
        for fix in self.fixes:
            symlink_path = fix['symlink_path']
            symlink_target = fix['symlink_target']

            if symlink_path not in created_symlinks:
                # Create parent directory if needed
                symlink_path.parent.mkdir(parents=True, exist_ok=True)

                # Remove if exists (might be a file, not symlink)
                if symlink_path.exists():
                    symlink_path.unlink()

                # Create symlink (use mklink on Windows, ln -s on Unix)
                try:
                    if platform.system() == 'Windows':
                        # Use mklink for Windows
                        cmd = ['mklink', str(symlink_path), str(symlink_target)]
                        subprocess.run(cmd, shell=True, check=True, capture_output=True)
                    else:
                        # Use ln -s for Unix/Linux
                        os.symlink(symlink_target, symlink_path)

                    created_symlinks.add(symlink_path)
                    print(f"[SYMLINK] {symlink_path.relative_to(self.project_root)}")
                    print(f"  -> {symlink_target}")
                except Exception as e:
                    print(f"[ERROR] Failed to create symlink {symlink_path}: {e}")

        # Update references in source files
        for source_file, fixes in by_source.items():
            if source_file not in updated_files:
                source_full = fixes[0]['source_full']

                try:
                    with open(source_full, 'r', encoding='utf-8') as f:
                        content = f.read()

                    original_content = content

                    # Replace all old references with new ones
                    for fix in fixes:
                        old_ref = fix['old_reference']
                        new_ref = fix['new_reference']
                        content = content.replace(old_ref, new_ref)

                    # Only write if changed
                    if content != original_content:
                        with open(source_full, 'w', encoding='utf-8') as f:
                            f.write(content)
                        updated_files.add(source_file)
                        print(f"[UPDATED] {source_file}")

                except Exception as e:
                    print(f"[ERROR] Failed to update {source_file}: {e}")

        print(f"\n[SUMMARY]")
        print(f"  Symlinks created: {len(created_symlinks)}")
        print(f"  Files updated: {len(updated_files)}")
        print(f"  Skipped (already exist): {len(self.skipped)}")

        return len(self.fixes)

    def print_preview(self) -> None:
        """Print preview of changes"""
        if not self.violations:
            print("[OK] No inside-plugin violations found!")
            return

        print(f"\n[PREVIEW] {len(self.violations)} violations to fix\n")

        # Group by plugin
        by_plugin = defaultdict(list)
        for v in self.violations:
            fix = self.propose_fix(v)
            if fix:
                by_plugin[v['plugin_name']].append(fix)
            else:
                self.skipped.append(v)

        for plugin_name in sorted(by_plugin.keys()):
            fixes = by_plugin[plugin_name]
            print(f"[PLUGIN] {plugin_name}: {len(fixes)} fixes")

            for fix in fixes[:3]:
                print(f"  FILE: {fix['source_file']}")
                print(f"  OLD: {fix['old_reference']}")
                print(f"  NEW: {fix['new_reference']}")
                print(f"  SYMLINK: {fix['symlink_path'].relative_to(self.project_root)}")
                print()

            if len(fixes) > 3:
                print(f"  ... and {len(fixes) - 3} more")
            print()

        print(f"\n[ACTION REQUIRED]")
        print(f"  Run with --apply flag to create symlinks and update references")

    def run(self, dry_run: bool = True) -> int:
        """Run the fixer"""
        self.analyze()

        if dry_run:
            self.print_preview()
        else:
            return self.apply_fixes()

        return len(self.violations)

def main() -> None:
    parser = argparse.ArgumentParser(description='Fix inside-plugin symlink violations')
    parser.add_argument('inventory', help='Path to inventory.json')
    parser.add_argument('--project', default='.', help='Project root')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes only')
    parser.add_argument('--apply', action='store_true', help='Apply fixes')

    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        args.dry_run = True

    fixer = InsidePluginSymlinkFixer(args.inventory, args.project)
    count = fixer.run(dry_run=args.dry_run)

    if args.apply:
        print(f"\n[DONE] Fixed {count} violations")

if __name__ == '__main__':
    main()
