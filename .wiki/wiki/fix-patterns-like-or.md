---
concept: fix-patterns-like-or
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/path-reference-auditor/scripts/cleanup_stacked_references.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.303155+00:00
cluster: skill
content_hash: 2859a435019c17c0
---

# Fix patterns like ./././ or ././././

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/path-reference-auditor/scripts/cleanup_stacked_references.py -->
#!/usr/bin/env python3
"""
cleanup_stacked_references.py
=====================================

Purpose:
    Fixes references that got cascading replacements like `././requirements.txt`
    into just `./requirements.txt` following installation or symlink repairs.

Layer: Investigate / Repair

Usage Examples:
    python scripts/cleanup_stacked_references.py --project . --dry-run
    python scripts/cleanup_stacked_references.py --project . --apply

Supported Object Types:
    Skill markdown files.

CLI Arguments:
    --project: Project root (default: .)
    --dry-run: Preview changes only (default: True if no action supplied)
    --apply: Apply fixes on disk

Input Files:
    - SKILL.md and documentation references files.

Output:
    Console logs of FIXED or WOULD FIX file paths.

Key Functions:
    - cleanup_stacked_paths()
    - process_skill_files()

Script Dependencies:
    - re
    - Path (pathlib)

Consumed by:
    Maintenance pipelines and post-symlink reconciliation workers.
"""

import re
from pathlib import Path
import argparse

def cleanup_stacked_paths(content: str) -> str:
    """Replace ./././ patterns with just ./ """
    # Fix patterns like ./././ or ././././
    content = re.sub(r'\./(\./)+([\w\-\.]+)', r'./\2', content)
    return content

def process_skill_files(project_root: str | Path, dry_run: bool = True) -> list[Path]:
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

def main() -> None:
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


<!-- Source: plugin-code/agent-scaffolders/scripts/cleanup_stacked_references.py -->
#!/usr/bin/env python
"""
cleanup_stacked_references.py
=====================================

Purpose:
    Fixes references that got cascading replacements like `././requirements.txt`
    into just `./requirements.txt` following installation or symlink repairs.

Layer: Investigate / Repair

Usage Examples:
    python scripts/cleanup_stacked_references.py --project . --dry-run
    python scripts/cleanup_stacked_references.py --project . --apply

Supported Object Types:
    Skill markdown files.

CLI Arguments:
    --project: Project root (default: .)
    --dry-run: Preview changes only (default: True if no action supplied)
    --apply: Apply fixes on disk

Input Files:
    - SKILL.md and documentation references files.

Output:
    Console logs of FIXED or WOULD FIX file paths.

Key Functions:
    - cleanup_stacked_paths()
    - process_skill_files()

Script Dependencies:
    - re
    - Path (pathlib)

Consumed by:
    Maintenance pipelines and post-symlink reconciliation workers.
"""

import re
from pathlib import Path
import argparse

def cleanup_stacked_paths(content: str) -> str:
    """Replace ./././ patterns with just ./ """
    # Fix patterns like ./././ or ././././
    content = re.sub(r'\./(\./)+([\w\-\.]+)', r'./\2', content)
    return content

def process_skill_files(project_root: str | Path, dry_run: bool = True) -> list[Path]:
    """Process all skill SKILL.md and references files"""
    project_path = Path(project_root)
    updated_files = []

    # Find all SKILL.md files in plugins/*/skills/
    skill_files = list(project_path.glob('plugins/*/skills/*/SKILL.m

*(combined content truncated)*

## See Also

- [[architectural-patterns-adapted-from-obrasuperpowers-mit-httpsgithubcomobrasuperpowers]]
- [[domain-patterns]]
- [[domain-patterns-exploration-cycle]]
- [[domain-patterns-exploration-session-failures]]
- [[domain-patterns-routing-skills]]
- [[fix-1-literal-n-chars-write-back-immediately-so-json-parse-can-proceed]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/path-reference-auditor/scripts/cleanup_stacked_references.py`
- **Indexed:** 2026-04-27T05:21:04.303155+00:00
