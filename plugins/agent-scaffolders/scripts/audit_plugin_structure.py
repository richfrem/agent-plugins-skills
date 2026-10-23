#!/usr/bin/env python3
"""
audit_plugin_structure.py
=====================================

Purpose:
    Validates plugin architecture, manifests, and component organization under APM:
    - Verifies apm.yml package manifest and .claude-plugin/plugin.json schema.
    - Prohibits raw filesystem symlinks in skills (APM packages require self-contained files).
    - Validates hub-and-spoke materialized copies against the copy-manifest (symlinks.json).
    - Flags drifted copies and unregistered duplicate files.
    - Prevents nested SKILL.md files.

Layer: Investigate / Codify / Audit

Usage Examples:
    python3 plugins/agent-scaffolders/scripts/audit_plugin_structure.py plugins/agent-scaffolders
    python3 plugins/agent-scaffolders/scripts/audit_plugin_structure.py .

Consumed by:
    Static auditor workflows, audit-plugin skill, and pre-flight validation gates.
"""

import json
import os
import sys
from pathlib import Path


SKIP_DIRS = {"evals", ".claude-plugin", "tests", "__pycache__"}
RESOURCE_DIRS = {"scripts", "references", "assets"}


def find_repo_root(start: Path) -> Path:
    """Walk up parents to locate the repository root containing symlinks.json or .git."""
    current = start.resolve()
    while current != current.parent:
        if (current / "symlinks.json").exists() or (current / ".git").exists():
            return current
        current = current.parent
    return start.resolve()


def load_copy_manifest(repo_root: Path) -> dict[str, str]:
    """Load symlinks.json copy-manifest entries: maps relative dst -> relative src."""
    manifest = repo_root / "symlinks.json"
    if not manifest.exists():
        return {}
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        links = data.get("links", [])
        result = {}
        for item in links:
            if item.get("strategy") == "copy":
                dst = str(Path(item["dst"])).replace("\\", "/")
                src = str(Path(item["src"])).replace("\\", "/")
                result[dst] = src
        return result
    except Exception:
        return {}


def audit_plugin(plugin_root: Path) -> list[dict]:
    """
    Audit a plugin directory for:
    - apm.yml package manifest
    - .claude-plugin/plugin.json schema conformance
    - Hub-and-spoke copy-manifest synchronization
    - Absence of raw symlinks and nested SKILL.md files
    """
    findings = []
    repo_root = find_repo_root(plugin_root)
    copy_map = load_copy_manifest(repo_root)

    # 1. Package Manifest Audits
    apm_manifest = plugin_root / "apm.yml"
    if not apm_manifest.exists():
        findings.append({
            "type": "missing_apm_manifest",
            "file": "apm.yml",
            "severity": "warning",
            "message": "Plugin root lacks apm.yml package manifest (required for APM distribution).",
        })

    claude_manifest = plugin_root / ".claude-plugin" / "plugin.json"
    if claude_manifest.exists():
        try:
            pj = json.loads(claude_manifest.read_text(encoding="utf-8"))
            author = pj.get("author")
            if not isinstance(author, dict) or not author.get("name"):
                findings.append({
                    "type": "invalid_author_schema",
                    "file": ".claude-plugin/plugin.json",
                    "severity": "error",
                    "message": "author must be an object with a 'name' field, e.g. {'name': '...', 'email': '...'}.",
                })
            for forbidden in ("skills", "agents", "hooks"):
                if forbidden in pj:
                    findings.append({
                        "type": "forbidden_manifest_key",
                        "file": ".claude-plugin/plugin.json",
                        "severity": "error",
                        "message": f"Do not declare '{forbidden}' in plugin.json; APM and Claude Code auto-discover components.",
                    })
        except Exception as e:
            findings.append({
                "type": "invalid_json_manifest",
                "file": ".claude-plugin/plugin.json",
                "severity": "error",
                "message": f"Invalid JSON in .claude-plugin/plugin.json: {e}",
            })

    # 2. Skills Directory Audit
    skills_dir = plugin_root / "skills"
    if not skills_dir.exists():
        return findings

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name in SKIP_DIRS:
            continue

        skill_entries = [skill_dir]
        for sub in skill_dir.iterdir():
            if sub.is_dir() and sub.name not in SKIP_DIRS and (sub / "SKILL.md").exists():
                skill_entries.append(sub)

        if not (skill_dir / "SKILL.md").exists():
            skill_entries = [e for e in skill_entries if e != skill_dir]

        for skill in skill_entries:
            for resource_dir_name in RESOURCE_DIRS:
                resource_dir = skill / resource_dir_name
                if not resource_dir.exists():
                    continue
                _scan_dir(resource_dir, skill, resource_dir_name, plugin_root, repo_root, copy_map, findings)

    return findings


def _scan_dir(
    directory: Path,
    skill: Path,
    resource_type: str,
    plugin_root: Path,
    repo_root: Path,
    copy_map: dict[str, str],
    findings: list,
    depth: int = 0,
) -> None:
    """Recursively scan a resource directory and enforce APM copy-manifest invariants."""
    for entry in sorted(directory.iterdir()):
        if entry.name.startswith(".") or entry.name in SKIP_DIRS:
            continue

        if entry.name == "SKILL.md":
            findings.append({
                "type": "nested_skill_file",
                "skill": str(skill.relative_to(plugin_root)),
                "resource_type": resource_type,
                "file": str(entry.relative_to(plugin_root)),
                "size": entry.stat().st_size if entry.exists() else 0,
                "severity": "error",
                "message": (
                    "SKILL.md must be the root file of a skill directory, "
                    "not a nested reference, script, or asset."
                ),
            })
            continue

        if entry.is_symlink():
            findings.append({
                "type": "raw_symlink_prohibited",
                "skill": str(skill.relative_to(plugin_root)),
                "resource_type": resource_type,
                "file": str(entry.relative_to(plugin_root)),
                "severity": "error",
                "message": (
                    "Raw filesystem symlinks are prohibited under APM. "
                    "Register the resource in symlinks.json (copy-manifest) and run materialize_copies.py."
                ),
            })
        elif entry.is_file():
            try:
                rel_repo_entry = str(entry.relative_to(repo_root)).replace("\\", "/")
            except ValueError:
                rel_repo_entry = ""

            if rel_repo_entry in copy_map:
                src_rel = copy_map[rel_repo_entry]
                src_path = repo_root / src_rel
                if not src_path.exists():
                    findings.append({
                        "type": "missing_copy_source",
                        "skill": str(skill.relative_to(plugin_root)),
                        "resource_type": resource_type,
                        "file": str(entry.relative_to(plugin_root)),
                        "severity": "error",
                        "message": f"Copy source defined in symlinks.json does not exist: {src_rel}",
                    })
                elif src_path.read_bytes() != entry.read_bytes():
                    findings.append({
                        "type": "drifted_copy",
                        "skill": str(skill.relative_to(plugin_root)),
                        "resource_type": resource_type,
                        "file": str(entry.relative_to(plugin_root)),
                        "severity": "error",
                        "message": (
                            f"Materialized copy has drifted from canonical source ({src_rel}). "
                            "Edit the canonical source and run materialize_copies.py to update."
                        ),
                    })
            else:
                try:
                    rel_skill_res = entry.relative_to(skill / resource_type)
                    matching_hub = plugin_root / resource_type / rel_skill_res
                    if matching_hub.exists() and matching_hub.is_file():
                        findings.append({
                            "type": "unregistered_duplicate",
                            "skill": str(skill.relative_to(plugin_root)),
                            "resource_type": resource_type,
                            "file": str(entry.relative_to(plugin_root)),
                            "severity": "error",
                            "message": (
                                f"File exists at plugin root ({resource_type}/{rel_skill_res}) but is not registered in symlinks.json. "
                                "Register it with strategy 'copy' to ensure centralized ownership."
                            ),
                        })
                except ValueError:
                    pass
        elif entry.is_dir():
            _scan_dir(entry, skill, resource_type, plugin_root, repo_root, copy_map, findings, depth + 1)


def suggest_fix(finding: dict, plugin_root: Path) -> None:
    """Print the commands needed to fix an audit finding."""
    ftype = finding.get("type")
    rel = finding.get("file", "")

    if ftype == "drifted_copy":
        print(f"\n  # Fix drifted copy: {rel}")
        print("  python3 plugins/agent-scaffolders/skills/convert-plugin-to-apm/scripts/materialize_copies.py")
    elif ftype == "raw_symlink_prohibited":
        print(f"\n  # Fix raw symlink: {rel}")
        print("  Add an entry to symlinks.json with strategy 'copy' and run materialize_copies.py")
    elif ftype == "unregistered_duplicate":
        print(f"\n  # Fix unregistered duplicate: {rel}")
        print("  Add an entry to symlinks.json with strategy 'copy' and run materialize_copies.py")
    elif ftype == "missing_apm_manifest":
        print(f"\n  # Fix missing apm.yml in {plugin_root.name}:")
        print("  Create apm.yml specifying package name, version, description, and targets.")


def main() -> None:
    """Parse CLI arguments and run the audit on the specified plugin directory."""
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
        print(f"\nERRORS ({len(errors)}):")
        for f in errors:
            print(f"  [{f['type']:25}] {f.get('file', '')} - {f['message']}")
        print(f"\nSuggested fixes:")
        for f in errors:
            suggest_fix(f, plugin_root)

    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for f in warnings:
            print(f"  [{f['type']:25}] {f.get('file', '')} - {f['message']}")

    print(f"\nSummary: {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
