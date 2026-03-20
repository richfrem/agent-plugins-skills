#!/usr/bin/env python3
"""
Path Reference Auditor
======================
Two-phase audit:
  Phase 1: SCAN - Find all ./references in code, populate inventory.json
  Phase 2: VERIFY - Read inventory.json, check if each reference exists in skill

Usage:
    # Phase 1: Discover all references
    python3 temp/path_reference_auditor.py --project . --phase scan

    # Phase 2: Verify each reference exists
    python3 temp/path_reference_auditor.py --project . --phase verify

    # Generate reports from verified inventory
    python3 temp/path_reference_auditor.py --project . --phase report --report missing
"""

import os
import re
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

class PathReferenceAuditor:
    def __init__(self, project_root, inventory_file='temp/inventory.json'):
        self.project_root = Path(project_root).resolve()
        self.inventory_file = Path(inventory_file)
        self.inventory = {
            "metadata": {
                "scanned_at": None,
                "verified_at": None,
                "project_root": str(self.project_root),
                "total_files_scanned": 0,
                "total_references_found": 0,
                "phase": "initial"
            },
            "references": []  # List of {source_file, reference, line, status}
        }

        # Patterns to find file references in code
        self.patterns = [
            r'\.\/([a-zA-Z0-9_\-/\.]+\.(md|mmd|py|json|sh|txt|in|yaml|yml))',  # ./path/to/file
            r'`([a-zA-Z0-9_\-/\.]+\.(md|mmd|py|json|sh|txt|in|yaml|yml))`',     # `path/to/file`
            r'\[([a-zA-Z0-9_\-/\.]+\.(md|mmd|py|json|sh|txt|in|yaml|yml))\]',   # [path/to/file]
            r'\(([a-zA-Z0-9_\-/\.]+\.(md|mmd|py|json|sh|txt|in|yaml|yml))\)',   # (path/to/file)
        ]

        self.file_extensions = {'.py', '.md', '.mmd', '.json', '.sh'}

    # ============================================================================
    # PHASE 1: SCAN - Find all references and populate inventory
    # ============================================================================

    def find_references_in_file(self, file_path):
        """Extract all path references from a single file."""
        references = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            for pattern in self.patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    ref_path = match.group(1)
                    line_num = content[:match.start()].count('\n') + 1

                    # Avoid duplicates in same file
                    if not any(r['reference'] == ref_path and r['line'] == line_num for r in references):
                        references.append({
                            'reference': ref_path,
                            'line': line_num
                        })
        except Exception as e:
            pass

        return references

    def phase_scan(self):
        """
        Phase 1: SCAN
        Walk all plugins/skills directories and find every ./reference.
        Populate inventory with raw reference data (no verification yet).
        """
        print(f"[FOLDER] Phase 1: SCAN - Finding all file references...")

        skills_dirs = [
            self.project_root / 'plugins',
            self.project_root / '.agents' / 'skills',
            self.project_root / '.agent' / 'skills',
            self.project_root / '.claude' / 'skills',
        ]

        scanned_files = 0
        total_refs = 0

        for skills_dir in skills_dirs:
            if not skills_dir.exists():
                continue

            for file_path in sorted(skills_dir.rglob('*')):
                if file_path.is_file() and file_path.suffix in self.file_extensions:
                    references = self.find_references_in_file(file_path)

                    if references:
                        scanned_files += 1
                        rel_path = str(file_path.relative_to(self.project_root))

                        for ref in references:
                            total_refs += 1
                            self.inventory['references'].append({
                                'source_file': rel_path,
                                'reference': ref['reference'],
                                'line': ref['line'],
                                'status': None  # Will be populated in Phase 2
                            })

        self.inventory['metadata']['scanned_at'] = datetime.now().isoformat()
        self.inventory['metadata']['total_files_scanned'] = scanned_files
        self.inventory['metadata']['total_references_found'] = total_refs
        self.inventory['metadata']['phase'] = 'scanned'

        print(f"  [OK] Scanned {scanned_files} files")
        print(f"  [OK] Found {total_refs} references")
        self.save_inventory()

    # ============================================================================
    # PHASE 2: VERIFY - Check if each reference exists in the skill
    # ============================================================================

    def check_reference_status(self, source_file, reference):
        """
        Check if a reference exists in the skill directory.
        Returns: {exists, type, path, details}
        """
        source_dir = Path(source_file).parent

        # Resolution paths to try (in order of priority)
        possible_paths = [
            source_dir / reference,                    # Relative to source file
            self.project_root / reference,             # Relative to project root
            source_dir.parent / reference,             # One level up
            source_dir.parent.parent / reference,      # Two levels up
        ]

        for path in possible_paths:
            try:
                resolved = path.resolve()

                if resolved.is_symlink():
                    target = resolved.resolve()
                    return {
                        'exists': True,
                        'type': 'symlink',
                        'path': str(resolved.relative_to(self.project_root)) if resolved.exists() else str(resolved),
                        'target': str(target.relative_to(self.project_root)) if target.exists() else 'BROKEN',
                        'resolved_path': str(resolved)
                    }
                elif resolved.exists():
                    return {
                        'exists': True,
                        'type': 'file' if resolved.is_file() else 'directory',
                        'path': str(resolved.relative_to(self.project_root)),
                        'resolved_path': str(resolved)
                    }
            except (ValueError, OSError):
                continue

        # Not found in any location
        return {
            'exists': False,
            'type': 'missing',
            'path': reference,
            'resolved_path': None
        }

    def phase_verify(self):
        """
        Phase 2: VERIFY
        Read inventory.json and check if each reference exists.
        Updates inventory with status information.
        """
        print(f"[OK] Phase 2: VERIFY - Checking if references exist...")

        if not self.inventory['references']:
            self.load_inventory()

        checked = 0
        for ref_item in self.inventory['references']:
            source_file = ref_item['source_file']
            reference = ref_item['reference']

            status = self.check_reference_status(source_file, reference)
            ref_item['status'] = status
            checked += 1

        self.inventory['metadata']['verified_at'] = datetime.now().isoformat()
        self.inventory['metadata']['phase'] = 'verified'

        print(f"  [OK] Verified {checked} references")
        self.save_inventory()

    # ============================================================================
    # REPORTING - Analyze verified inventory
    # ============================================================================

    def get_missing_references(self):
        """Get all missing references."""
        return [r for r in self.inventory['references'] if r['status'] and not r['status']['exists']]

    def get_symlinks(self):
        """Get all symlink references."""
        return [r for r in self.inventory['references'] if r['status'] and r['status']['type'] == 'symlink']

    def get_broken_symlinks(self):
        """Get all broken symlinks."""
        return [r for r in self.inventory['references']
                if r['status'] and r['status']['type'] == 'symlink' and r['status']['target'] == 'BROKEN']

    def get_valid_references(self):
        """Get all valid (existing) references."""
        return [r for r in self.inventory['references'] if r['status'] and r['status']['exists']]

    def phase_report(self, report_type='summary'):
        """
        Phase 3: REPORT
        Generate analysis reports from verified inventory.
        """
        if not self.inventory['references'] or self.inventory['references'][0].get('status') is None:
            self.load_inventory()

        if report_type == 'summary':
            total = len(self.inventory['references'])
            valid = len(self.get_valid_references())
            missing = len(self.get_missing_references())
            symlinks = len(self.get_symlinks())
            broken = len(self.get_broken_symlinks())

            print(f"\n[REPORT] Audit Summary:")
            print(f"  Files scanned: {self.inventory['metadata']['total_files_scanned']}")
            print(f"  Total references: {total}")
            print(f"  [OK] Valid: {valid}")
            print(f"  [ERROR] Missing: {missing}")
            print(f"  [LINK] Symlinks: {symlinks}")
            print(f"  [LINK] Broken symlinks: {broken}")

        elif report_type == 'missing':
            items = self.get_missing_references()
            print(f"\n[ERROR] Missing References ({len(items)}):")
            for item in sorted(items, key=lambda x: x['source_file']):
                print(f"  {item['source_file']}:{item['line']}")
                print(f"      {item['reference']}")

        elif report_type == 'broken_symlinks':
            items = self.get_broken_symlinks()
            print(f"\n[LINK] Broken Symlinks ({len(items)}):")
            for item in sorted(items, key=lambda x: x['source_file']):
                print(f"  {item['source_file']}:{item['line']}")
                print(f"      {item['reference']}")
                print(f"     Target: {item['status']['target']}")

        elif report_type == 'symlinks':
            items = self.get_symlinks()
            print(f"\n[LINK] All Symlinks ({len(items)}):")
            for item in sorted(items, key=lambda x: x['source_file']):
                status = item['status']
                state = "[OK]" if status['target'] != 'BROKEN' else "[ERROR]"
                print(f"  {state} {item['source_file']}:{item['line']}")
                print(f"     Ref: {item['reference']}")
                print(f"     Target: {status['target']}")

        elif report_type == 'all':
            self.phase_report('summary')
            self.phase_report('missing')
            self.phase_report('broken_symlinks')

    # ============================================================================
    # PERSISTENCE
    # ============================================================================

    def save_inventory(self):
        """Save inventory to JSON file."""
        self.inventory_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.inventory_file, 'w') as f:
            json.dump(self.inventory, f, indent=2)
        print(f"  [OK] Inventory saved: {self.inventory_file}")

    def load_inventory(self):
        """Load inventory from JSON file."""
        if not self.inventory_file.exists():
            print(f"[ERROR] Inventory not found: {self.inventory_file}")
            print(f"   Run with --phase scan first")
            sys.exit(1)
        with open(self.inventory_file, 'r') as f:
            self.inventory = json.load(f)


def main():
    parser = argparse.ArgumentParser(description='Path Reference Auditor - 2 Phase Audit')
    parser.add_argument('--project', required=True, help='Project root directory')
    parser.add_argument('--phase', choices=['scan', 'verify', 'report'], required=True,
                       help='Audit phase: scan (find refs)  verify (check exists)  report (analyze)')
    parser.add_argument('--report', choices=['summary', 'missing', 'broken_symlinks', 'symlinks', 'all'],
                       default='summary', help='Report type (for --phase report)')
    parser.add_argument('--inventory', default='temp/inventory.json', help='Inventory file path')

    args = parser.parse_args()

    auditor = PathReferenceAuditor(args.project, args.inventory)

    if args.phase == 'scan':
        auditor.phase_scan()

    elif args.phase == 'verify':
        auditor.phase_verify()

    elif args.phase == 'report':
        auditor.phase_report(args.report)


if __name__ == '__main__':
    main()
