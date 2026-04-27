---
concept: handle-nested-skills-eg-skillsdeferredskill
source: plugin-code
source_file: agent-scaffolders/scripts/audit_plugin_structure.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.818933+00:00
cluster: skill
content_hash: fce1e67abcfbd9ee
---

# Handle nested skills (e.g. skills/deferred/<skill>)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
audit_plugin_structure.py
=====================================

Purpose:
    Scans a plugin directory and flags any scripts, references, or assets that
    live directly inside a skill directory rather than at the plugin root.
    Promotes consolidating assets into plugin root structures with local symlinks.

Layer: Investigate / Codify / Audit

Usage Examples:
    pythonaudit_plugin_structure.py plugins/agent-scaffolders
    pythonaudit_plugin_structure.py .

Supported Object Types:
    Plugin folder trees.

CLI Arguments:
    plugin-dir: Position argument for the root of the plugin directory tree.

Input Files:
    None.

Output:
    Console logs listing ERRORS (real files) and WARNINGS (broken symlinks).

Key Functions:
    - audit_plugin()
    - _scan_dir()
    - suggest_fix()

Script Dependencies:
    - os
    - sys
    - pathlib

Consumed by:
    Static auditor workflows and pre-flight validation hooks.
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
) -> None:
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
        elif entry.is_di

*(content truncated)*

## See Also

- [[1-handle-absolute-paths-from-repo-root]]
- [[attempt-to-handle-langchain-version-differences-for-storage]]
- [[domain-patterns-routing-skills]]
- [[handle-yaml-multiline-indicators]]
- [[initialize-empty-hooks-schema-in-a-nested-hooks-dir]]
- [[install-plugin-in-a-different-repo-eg-context-bundler-specifically]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/audit_plugin_structure.py`
- **Indexed:** 2026-04-27T05:21:03.818933+00:00
