#!/usr/bin/env python3
"""
audit_plugin_structure.py

Scans a plugin directory and flags any scripts, references, or assets that
live inside a skill directory rather than at the plugin root.

These should be:
  1. Moved to the plugin root (scripts/, references/, assets/)
  2. Replaced with a file-level symlink inside the skill pointing to plugin root

Usage:
    python3 audit_plugin_structure.py <plugin-dir>
    python3 audit_plugin_structure.py .
"""

import os
import sys
from pathlib import Path


SKIP_DIRS = {"evals", ".claude-plugin", "tests", "__pycache__"}
RESOURCE_DIRS = {"scripts", "references", "assets"}


def audit_plugin(plugin_root: Path) -> list[dict]:
    """
    Walk all skills and return findings for any resource files that are
    real files (not symlinks) inside a skill directory.
    """
    findings = []
    skills_dir = plugin_root / "skills"

    if not skills_dir.exists():
        return findings

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name in SKIP_DIRS:
            continue
        # Handle nested skills (e.g. skills/deferred/<skill>)
        skill_entries = [skill_dir]
        for sub in skill_dir.iterdir():
            if sub.is_dir() and sub.name not in SKIP_DIRS and (sub / "SKILL.md").exists():
                skill_entries.append(sub)
        # If skill_dir itself has no SKILL.md it may be a grouping dir
        if not (skill_dir / "SKILL.md").exists():
            skill_entries = [e for e in skill_entries if e != skill_dir]

        for skill in skill_entries:
            for resource_dir_name in RESOURCE_DIRS:
                resource_dir = skill / resource_dir_name
                if not resource_dir.exists():
                    continue
                _scan_dir(resource_dir, skill, resource_dir_name, plugin_root, findings)

    return findings


def _scan_dir(
    directory: Path,
    skill: Path,
    resource_type: str,
    plugin_root: Path,
    findings: list,
    depth: int = 0,
):
    for entry in sorted(directory.iterdir()):
        if entry.name.startswith(".") or entry.name in SKIP_DIRS:
            continue
        if entry.is_symlink():
            target = entry.resolve()
            # Check if symlink points inside plugin root (good) or elsewhere (warn)
            try:
                target.relative_to(plugin_root)
                in_plugin = True
            except ValueError:
                in_plugin = False
            if not in_plugin:
                findings.append({
                    "type": "broken_symlink_target",
                    "skill": str(skill.relative_to(plugin_root)),
                    "file": str(entry.relative_to(plugin_root)),
                    "target": str(target),
                    "severity": "warning",
                    "message": f"Symlink points outside plugin root: {target}",
                })
        elif entry.is_file():
            findings.append({
                "type": "real_file_in_skill",
                "skill": str(skill.relative_to(plugin_root)),
                "resource_type": resource_type,
                "file": str(entry.relative_to(plugin_root)),
                "size": entry.stat().st_size,
                "severity": "error",
                "message": (
                    f"Real file found in skill {resource_type}/. "
                    f"Move to plugin root {resource_type}/ and replace with symlink."
                ),
            })
        elif entry.is_dir():
            _scan_dir(entry, skill, resource_type, plugin_root, findings, depth + 1)


def suggest_fix(finding: dict, plugin_root: Path):
    """Print the commands needed to fix a real-file finding."""
    rel = finding["file"]
    parts = Path(rel).parts
    # e.g. skills/my-skill/scripts/foo.py  or  skills/my-skill/references/sub/foo.md
    # Find resource dir index
    for i, p in enumerate(parts):
        if p in RESOURCE_DIRS:
            resource_type = p
            sub_path = Path(*parts[i + 1:])  # path after scripts/references/assets/
            break
    else:
        return

    plugin_dest = plugin_root / resource_type / sub_path
    skill_file = plugin_root / rel

    # Symlink depth: from skill file location back to plugin root
    skill_file_parts = len(skill_file.relative_to(plugin_root).parts)
    # depth = number of dirs above the file = skill_file_parts - 1 (subtract filename)
    up = "../" * (skill_file_parts - 1)
    symlink_target = f"{up}{resource_type}/{sub_path}"

    print(f"\n  # Fix: {rel}")
    if not plugin_dest.parent.exists():
        print(f"  mkdir -p {plugin_dest.parent.relative_to(plugin_root)}")
    print(f"  mv {rel} {resource_type}/{sub_path}")
    print(f"  ln -s {symlink_target} {rel}")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <plugin-dir>")
        sys.exit(1)

    plugin_root = Path(sys.argv[1]).resolve()
    if not plugin_root.exists():
        print(f"Error: {plugin_root} does not exist")
        sys.exit(1)

    findings = audit_plugin(plugin_root)
    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]

    if not findings:
        print(f"OK  {plugin_root.name}: no violations found")
        sys.exit(0)

    print(f"\nPlugin: {plugin_root.name}")
    print(f"{'=' * 60}")

    if errors:
        print(f"\nERRORS ({len(errors)}) - real files inside skill dirs:")
        for f in errors:
            print(f"  [{f['resource_type']:10}] {f['file']}  ({f['size']} bytes)")
        print(f"\nSuggested fixes (run from plugin root):")
        for f in errors:
            suggest_fix(f, plugin_root)

    if warnings:
        print(f"\nWARNINGS ({len(warnings)}) - symlinks pointing outside plugin root:")
        for f in warnings:
            print(f"  {f['file']} -> {f['target']}")

    print(f"\nSummary: {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
