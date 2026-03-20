#!/usr/bin/env python3
"""
Cleanup Stacked References
===========================
Fixes references that got cascading replacements like ././requirements.txt

When symlinks exist at skill level, references should just be the filename.

Usage:
    python scripts/cleanup_stacked_references.py --project . --dry-run
    python scripts/cleanup_stacked_references.py --project . --apply
"""

import re
from pathlib import Path
import argparse

def cleanup_stacked_paths(content):
    """Replace ./././ patterns with just ./ """
    # Fix patterns like ./././ or ././././
    content = re.sub(r'\./(\./)+([\w\-\.]+)', r'./\2', content)
    return content

def process_skill_files(project_root, dry_run=True):
    """Process all skill SKILL.md and references files"""
    project_path = Path(project_root)
    updated_files = []

    # Find all SKILL.md files in plugins/*/skills/
    skill_files = list(project_path.glob('plugins/*/skills/*/SKILL.md'))
    skill_files += list(project_path.glob('plugins/*/skills/*/*/*.md'))

    for skill_file in skill_files:
        try:
            with open(skill_file, 'r', encoding='utf-8') as f:
                original_content = f.read()

            cleaned_content = cleanup_stacked_paths(original_content)

            if cleaned_content != original_content:
                if not dry_run:
                    with open(skill_file, 'w', encoding='utf-8') as f:
                        f.write(cleaned_content)
                    print(f"[FIXED] {skill_file.relative_to(project_path)}")
                else:
                    print(f"[WOULD FIX] {skill_file.relative_to(project_path)}")
                updated_files.append(skill_file)
        except Exception as e:
            print(f"[ERROR] {skill_file}: {e}")

    return updated_files

def main():
    parser = argparse.ArgumentParser(description='Cleanup stacked reference paths')
    parser.add_argument('--project', default='.', help='Project root')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes only')
    parser.add_argument('--apply', action='store_true', help='Apply fixes')

    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        args.dry_run = True

    print(f"\n[CLEANUP] Fixing stacked reference paths\n")
    updated = process_skill_files(args.project, dry_run=args.dry_run)

    print(f"\n[SUMMARY] {len(updated)} files with stacked paths")
    if args.dry_run:
        print("Run with --apply to fix")

if __name__ == '__main__':
    main()
