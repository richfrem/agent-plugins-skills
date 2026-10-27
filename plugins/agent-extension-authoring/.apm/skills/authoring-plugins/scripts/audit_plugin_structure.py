#!/usr/bin/env python3
"""
audit_plugin_structure.py
=====================================

Purpose:
    Validates plugin architecture, manifests, and component organization under APM:
    - Verifies apm.yml package manifest and .claude-plugin/plugin.json schema.
    - Enforces single primitive root under .apm/ (no duplicate root skills/, agents/, hooks/, etc.).
    - Validates lsp.json / .lsp.json format per SF-10.
    - Prohibits raw filesystem symlinks in skills (APM packages require self-contained files).
    - Validates transitional copy-manifest entries (symlinks.json) if present and flags unregistered duplicates.
    - Prevents nested SKILL.md files.

Layer: Investigate / Codify / Audit

Usage Examples:
    python3 plugins/agent-extension-authoring/.apm/skills/authoring-plugins/scripts/audit_plugin_structure.py plugins/agent-extension-authoring
    python3 plugins/agent-extension-authoring/.apm/skills/authoring-plugins/scripts/audit_plugin_structure.py .

Consumed by:
    Static auditor workflows, authoring-plugins skill, and pre-flight validation gates.
"""

import json
import os
import sys
from pathlib import Path


SKIP_DIRS = {"evals", ".claude-plugin", "tests", "__pycache__"}
RESOURCE_DIRS = {"scripts", "references", "assets"}
PRIMITIVE_DIRS = ("skills", "agents", "hooks", "prompts", "instructions")


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


def _check_lsp_json(plugin_root: Path, findings: list[dict]) -> None:
    """Check lsp.json / .lsp.json against SF-10 (flat map of serverName -> {command, ...})."""
    for lsp_name in ("lsp.json", ".lsp.json"):
        lsp_path = plugin_root / lsp_name
        if not lsp_path.is_file():
            continue
        try:
            data = json.loads(lsp_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or not data:
                findings.append({
                    "type": "invalid_lsp_json",
                    "file": lsp_name,
                    "severity": "warning",
                    "message": f"{lsp_name} is empty or not an object; remove placeholder or declare flat server entries (SF-10).",
                })
            elif "languageServers" in data:
                findings.append({
                    "type": "invalid_lsp_json",
                    "file": lsp_name,
                    "severity": "error",
                    "message": f"{lsp_name} wraps servers in 'languageServers'; Claude Code requires a flat map {{serverName: {{command, ...}}}} (SF-10).",
                })
            else:
                for srv_name, srv_cfg in data.items():
                    if not isinstance(srv_cfg, dict) or not srv_cfg.get("command"):
                        findings.append({
                            "type": "invalid_lsp_json",
                            "file": lsp_name,
                            "severity": "error",
                            "message": f"{lsp_name} server '{srv_name}' must be an object with a non-empty 'command' (SF-10).",
                        })
        except Exception as e:
            findings.append({
                "type": "invalid_lsp_json",
                "file": lsp_name,
                "severity": "error",
                "message": f"Invalid JSON in {lsp_name}: {e}",
            })


def audit_plugin(plugin_root: Path) -> list[dict]:
    """
    Audit a plugin directory for:
    - apm.yml package manifest
    - .claude-plugin/plugin.json schema conformance
    - .apm/ primitive root unification (no duplicate root skills/agents/hooks)
    - lsp.json conformance (SF-10)
    - Absence of raw symlinks, unregistered duplicates, and nested SKILL.md files
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
            for forbidden in ("skills", "agents", "hooks", "commands"):
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

    _check_lsp_json(plugin_root, findings)

    # 2. Primitive Root Unification Audit
    has_apm_dir = (plugin_root / ".apm").is_dir()
    for prim in PRIMITIVE_DIRS:
        apm_prim = plugin_root / ".apm" / prim
        root_prim = plugin_root / prim
        if root_prim.exists() and (apm_prim.exists() or has_apm_dir):
            findings.append({
                "type": "duplicate_primitive_root",
                "rule": "duplicate-primitive-root",
                "file": str(root_prim),
                "severity": "error",
                "message": f"Duplicate '{prim}/' directory found outside '.apm/'. In APM-native packages, primitives belong exclusively in '.apm/{prim}/'.",
            })

    apm_skills = plugin_root / ".apm" / "skills"
    root_skills = plugin_root / "skills"
    skills_dir = apm_skills if apm_skills.exists() else root_skills
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
    """Recursively scan a resource directory and enforce self-contained APM skill invariants."""
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
                    "Raw filesystem symlinks are prohibited under APM (SF-2). "
                    "Replace with a real self-contained file inside the skill directory."
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
                            "Consolidate into a self-contained skill file or sync via materialize_copies.py."
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
                                f"File also exists at plugin root ({resource_type}/{rel_skill_res}). "
                                "Remove the plugin-root duplicate so the skill in .apm/skills/ is the single self-contained owner."
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
        print("  Consolidate into a single owning skill under .apm/skills/ or run materialize_copies.py if mid-migration.")
    elif ftype == "raw_symlink_prohibited":
        print(f"\n  # Fix raw symlink: {rel}")
        print("  Replace the symlink with a real file inside .apm/skills/<skill>/ (SF-2).")
    elif ftype == "unregistered_duplicate":
        print(f"\n  # Fix duplicate plugin-root file: {rel}")
        print("  Remove the plugin-root copy and keep the file solely inside .apm/skills/<skill>/.")
    elif ftype == "duplicate_primitive_root":
        print(f"\n  # Fix duplicate primitive directory: {rel}")
        print("  Move all primitives into .apm/ and remove the root duplicate directory.")
    elif ftype == "missing_apm_manifest":
        print(f"\n  # Fix missing apm.yml in {plugin_root.name}:")
        print("  Create apm.yml specifying package name, version, description, author, and license.")


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
    errors = [f for f in findings if f.get("severity") == "error"]
    warnings = [f for f in findings if f.get("severity") == "warning"]

    if not findings:
        print(f"OK  {plugin_root.name}: no violations found")
        sys.exit(0)

    print(f"\nPlugin: {plugin_root.name}")
    print(f"{'=' * 60}")

    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for f in errors:
            print(f"  [{f.get('type', 'error'):25}] {f.get('file', '')} - {f['message']}")
        print(f"\nSuggested fixes:")
        for f in errors:
            suggest_fix(f, plugin_root)

    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for f in warnings:
            print(f"  [{f.get('type', 'warning'):25}] {f.get('file', '')} - {f['message']}")

    print(f"\nSummary: {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
