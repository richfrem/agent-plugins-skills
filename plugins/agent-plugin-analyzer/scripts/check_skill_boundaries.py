#!/usr/bin/env python3
"""
check_skill_boundaries.py
=====================================

Purpose:
    Flags any internal file references inside a skill directory that point
    OUTSIDE their self-contained boundaries to ensure distribution safety.

Layer: Investigate / Codify / Audit

Usage Examples:
    python3 check_skill_boundaries.py temp/inventory.json --batch all
    python3 check_skill_boundaries.py temp/inventory.json --skill plugins/adr-manager/skills/adr-management

Supported Object Types:
    Skill file references.

CLI Arguments:
    inventory: Path to inventory.json (Required)
    --project: Project root directory (default: .)
    --skill: Skill path or name to check (default: all)
    --batch: Batch mode all or specific skill (default: all)

Input Files:
    - inventory.json

Output:
    Console logs listing BOUNDARY VIOLATIONS.

Key Functions:
    - is_whitelisted()
    - get_skill_root()
    - is_reference_inside_skill()
    - filter_references()

Script Dependencies:
    - json
    - sys
    - argparse
    - re
    - Path (pathlib)

Consumed by:
    Static auditor workflows and path reference audits.
"""

import json
import sys
import argparse
import re
from pathlib import Path

# ==============================================================================
# WHITELIST — references that should never be flagged as violations.
# These are example paths used in documentation to explain concepts,
# not real file references that need to exist.
# Add patterns here as plain strings (exact match) or regex (prefixed with "re:").
# ==============================================================================
WHITELIST = [
    # Example absolute paths from documentation/other machines
    r"re:/Users/.*",           # macOS absolute paths (e.g. /Users/robert/...)
    r"re:/home/.*",            # Linux absolute paths
    r"re:/tasks/.*",           # Example task paths
    r"re:/.kittify/.*",        # Example kittify runtime paths
    r"re:/[a-zA-Z]:/.*",       # Windows absolute paths (e.g. C:/...)
    # Example placeholder filenames used in docs
    "path/to/file.md",
    "path/to/file.py",
    "my-skill/SKILL.md",
    "my-plugin",
    # kitty-specs example paths
    r"re:.*kitty-specs/.*",
    # Dead-link documentation references (files referenced in docs but never created)
    r"re:.*requirements-core\.in",     # dependency-management docs example path
    r"re:.*infinite-context-ecosystem\.mmd",  # rlm-* BLUEPRINT/research docs
    r"re:.*infinite-context-ecosystem\.png",  # same diagram, png variant
    r"re:.*Agent_Workflow_Orchestration_Design\.md",  # architecture doc never created
]

def is_whitelisted(reference: str) -> bool:
    """Return True if the reference matches any whitelist pattern."""
    for pattern in WHITELIST:
        if pattern.startswith("re:"):
            if re.match(pattern[3:], reference):
                return True
        else:
            if reference == pattern or reference.startswith(pattern):
                return True
    return False

def get_skill_root(source_file_path: str) -> Path | None:
    """
    Extract the skill root directory from a source file path.

    Examples:
      plugins/adr-manager/skills/adr-management/SKILL.md
       plugins/adr-manager/skills/adr-management/

      .agents/skills/plugin-installer/SKILL.md
       .agents/skills/plugin-installer/
    """
    parts = Path(source_file_path).parts

    # Find "skills" in the path
    if "skills" in parts:
        idx = list(parts).index("skills")
        # The skill root is skills/<skill-name>/
        if idx + 1 < len(parts):
            return Path(*parts[:idx+2])  # e.g., plugins/adr-manager/skills/adr-management

    return None

def is_reference_inside_skill(source_file: str, reference: str, project_root: str | Path) -> tuple[bool | None, Path | None, Path | None]:
    """
    Check if a reference stays within the skill directory.

    Returns: (is_inside, resolved_path, skill_root)
    """
    project_root = Path(project_root)
    source_path = project_root / source_file
    source_dir = source_path.parent
    skill_root = get_skill_root(source_file)

    if not skill_root:
        return None, None, None

    skill_root_abs = project_root / skill_root

    # Try to resolve the reference
    try:
        candidate = source_dir / reference
        skill_root_resolved = skill_root_abs.resolve()

        # If a symlink or file exists at the candidate path AND it lives inside
        # the skill directory, treat it as inside. Symlinks placed inside a skill
        # are intentional bridges — do NOT follow them to their targets.
        candidate_abs = candidate.absolute()
        if str(candidate_abs).startswith(str(skill_root_resolved)):
            return True, candidate_abs, skill_root_resolved

        # Fall back: fully resolve (follows symlinks) for non-symlink cases
        resolved = candidate.resolve()
        is_inside = str(resolved).startswith(str(skill_root_resolved))

        return is_inside, resolved, skill_root_resolved
    except:
        return False, None, skill_root_abs

def filter_references(references: list[dict], skill_filter: str) -> list[dict]:
    """Filter references by skill path or name."""
    if not skill_filter or skill_filter.lower() == 'all':
        return references

    filtered = []
    for ref in references:
        source_file = ref['source_file']
        skill_root = get_skill_root(source_file)

        if not skill_root:
            continue

        # Match by full path or skill name
        skill_str = str(skill_root)
        if skill_filter in skill_str or skill_str.endswith(skill_filter):
            filtered.append(ref)

    return filtered

def main() -> int:
    parser = argparse.ArgumentParser(description='Skill Boundary Checker')
    parser.add_argument('inventory', help='Path to inventory.json')
    parser.add_argument('--project', default='.', help='Project root directory')
    parser.add_argument('--skill', default='all', help='Skill path or name to check (default: all)')
    parser.add_argument('--batch', default='all', help='Batch mode: all or specific skill')

    args = parser.parse_args()

    # Use --skill if provided, otherwise --batch
    skill_filter = args.skill if args.skill != 'all' else args.batch

    try:
        with open(args.inventory, 'r') as f:
            inventory = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Inventory not found: {args.inventory}")
        sys.exit(1)

    references = inventory.get('references', [])

    # Filter references
    filtered = filter_references(references, skill_filter)

    print(f"[SYMBOL] Checking {len(filtered)} references for skill boundary violations")
    if skill_filter != 'all':
        print(f"   (filtered to: {skill_filter})\n")
    else:
        print()

    violations = []
    inside_count = 0
    whitelisted_count = 0

    for ref_item in filtered:
        source_file = ref_item['source_file']
        reference = ref_item['reference']
        line = ref_item['line']

        # Skip whitelisted example/documentation references
        if is_whitelisted(reference):
            whitelisted_count += 1
            continue

        is_inside, resolved, skill_root = is_reference_inside_skill(source_file, reference, args.project)

        if is_inside is None:
            continue  # Not a skill file
        elif is_inside:
            inside_count += 1
        else:
            violations.append({
                'source_file': source_file,
                'reference': reference,
                'line': line,
                'resolved': str(resolved) if resolved else None,
                'skill_root': str(skill_root) if skill_root else None
            })

    # Report violations
    if violations:
        print(f"[ERROR] VIOLATIONS FOUND: {len(violations)} references point OUTSIDE their skill\n")

        for v in sorted(violations, key=lambda x: x['source_file']):
            print(f"FILE: {v['source_file']}:{v['line']}")
            print(f"  REF: {v['reference']}")
            print(f"  SKILL ROOT: {v['skill_root']}")
            print(f"  RESOLVES TO: {v['resolved']}")
            print()
    else:
        print(f"[SYMBOL] No violations found!\n")

    print(f"[SYMBOL] Summary:")
    print(f"  Checked: {len(filtered)} references")
    print(f"  Inside skill: {inside_count}")
    print(f"  Whitelisted (examples/docs): {whitelisted_count}")
    print(f"  Outside skill (violations): {len(violations)}")

    return 0 if not violations else 1

if __name__ == '__main__':
    sys.exit(main())
