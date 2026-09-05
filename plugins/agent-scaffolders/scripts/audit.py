#!/usr/bin/env python
"""
audit.py (CLI)
=====================================

Purpose:
    Audit plugins against the Agent Skills Open Standard to ensure architectural and resource compliance.

Layer: Meta-Execution

Usage Examples:
    python audit.py --path <plugin-directory>

Supported Object Types:
    - .claude-plugin formatted directories
    - Agent Skills

CLI Arguments:
    --path: The absolute or relative path to the plugin directory to audit.

Input Files:
    - ./plugin.json
    - ././SKILL.md files
    - .mcp.json and hooks.json structures

Output:
    - Terminal stdout (Success/Fail metrics)
    - Warnings for minor structural deviations

Key Functions:
    - audit_plugin(): Recursively checks directory presence and constraints.

Script Dependencies:
    None

Consumed by:
    - User (CLI)
    - ecosystem-standards (Agent Skill)
"""
import argparse
import os
import json
import glob
import sys

# Ensure Unicode output works on Windows terminals that default to cp1252
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def _is_deprecated_stub(plugin_path: str) -> bool:
    """Detect deprecated stub plugins (no skills/ directory + README marked DEPRECATED)."""
    skills_dir_check = os.path.join(plugin_path, "skills")
    readme_check = os.path.join(plugin_path, "README.md")
    if os.path.isdir(skills_dir_check):
        return False
    if os.path.isfile(readme_check):
        with open(readme_check, "r", encoding="utf-8") as f:
            if "DEPRECATED" in f.read():
                return True
    return False


def _check_root_structure(plugin_path: str, errors: list, warnings: list) -> None:
    """Check .claude-plugin/plugin.json presence, schema compliance, legacy file placement, and root README."""
    claude_plugin_dir = os.path.join(plugin_path, ".claude-plugin")
    manifest_path = None
    if os.path.isdir(claude_plugin_dir):
        candidate = os.path.join(claude_plugin_dir, "plugin.json")
        if os.path.isfile(candidate):
            manifest_path = candidate
        else:
            errors.append("Missing `plugin.json` inside `.claude-plugin/`.")
    elif os.path.isfile(os.path.join(plugin_path, "plugin.json")):
        manifest_path = os.path.join(plugin_path, "plugin.json")
    else:
        errors.append("Missing `.claude-plugin/` directory and `plugin.json`.")

    if manifest_path:
        # Check for duplicate keys and valid JSON
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                raw_text = f.read()

            def strict_duplicate_check(ordered_pairs):
                """Raise on any duplicate JSON key instead of silently keeping the last one."""
                d = {}
                for k, v in ordered_pairs:
                    if k in d:
                        errors.append(f"Duplicate top-level key '{k}' in `{os.path.relpath(manifest_path, plugin_path)}`.")
                    d[k] = v
                return d

            data = json.loads(raw_text, object_pairs_hook=strict_duplicate_check)

            # Strict Claude Code Schema: Banned fields (must be auto-discovered by Claude Code)
            banned_fields = ["skills", "agents", "hooks", "commands"]
            for field in banned_fields:
                if field in data:
                    errors.append(f"`.claude-plugin/plugin.json` must NOT contain `{field}` array or property; Claude Code auto-discovers {field}.")

            # Check author format: must be an object with a "name" key
            if "author" in data:
                author = data["author"]
                if not isinstance(author, dict):
                    errors.append(f"`author` in `{os.path.relpath(manifest_path, plugin_path)}` must be an object (`{{\"name\": \"...\", \"email\": \"...\"}}`), not {type(author).__name__}.")
                elif not author.get("name") or not isinstance(author.get("name"), str):
                    errors.append(f"`author` object in `{os.path.relpath(manifest_path, plugin_path)}` must contain a non-empty string for `name`.")
            else:
                errors.append(f"Missing required `author` object in `{os.path.relpath(manifest_path, plugin_path)}` (must be `{{\"name\": \"...\", \"email\": \"...\"}}`).")

        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in `{os.path.relpath(manifest_path, plugin_path)}`: {e}")
        except Exception as e:
            errors.append(f"Error reading `{os.path.relpath(manifest_path, plugin_path)}`: {e}")

    if os.path.isfile(os.path.join(plugin_path, "mcp.json")):
        errors.append("Found `mcp.json` at root. The officially supported standard is `.mcp.json`.")
    if os.path.isfile(os.path.join(plugin_path, "hooks.json")):
        errors.append("Found `hooks.json` at root. The officially supported standard requires `hooks/hooks.json`.")

    readme_path = os.path.join(plugin_path, "README.md")
    if not os.path.isfile(readme_path):
        warnings.append("Missing root `README.md`.")
    else:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "├──" not in content and "└──" not in content:
                warnings.append("The `README.md` is missing a file tree structure. It is highly recommended to include one.")


def _check_skills(plugin_path: str, errors: list, warnings: list) -> None:
    """Check each skill directory for SKILL.md, references/, and illegal root directories."""
    skills_dir = os.path.join(plugin_path, "skills")
    if not os.path.isdir(skills_dir):
        return

    try:
        from audit_skill import audit_skill
    except ImportError:
        sys.path.insert(0, os.path.dirname(__file__))
        try:
            from audit_skill import audit_skill
        except ImportError:
            audit_skill = None

    for skill_name in os.listdir(skills_dir):
        skill_path = os.path.join(skills_dir, skill_name)
        if not os.path.isdir(skill_path):
            continue

        skill_md = os.path.realpath(os.path.join(skill_path, "././SKILL.md"))

        if not os.path.isfile(skill_md):
            errors.append(f"Skill '{skill_name}' is missing `././SKILL.md`.")
        elif audit_skill:
            skill_res = audit_skill(skill_path, plugin_root=plugin_path)
            for err in skill_res.errors:
                if "missing required SKILL.md" not in err.lower():
                    errors.append(f"Skill '{skill_name}': {err}")
            for warn in skill_res.warnings:
                warnings.append(f"Skill '{skill_name}': {warn}")
        else:
            with open(skill_md, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) > 500:
                    warnings.append(f"Skill '{skill_name}' ././SKILL.md exceeds 500 lines ({len(lines)} lines). Extract logic to scripts.")

        # Check for Microsoft Progressive Disclosure & Testing standard
        references_dir = os.path.realpath(os.path.join(skill_path, "references"))
        if not os.path.isdir(references_dir):
            warnings.append(f"Skill '{skill_name}' is missing a `references/` directory. Progressive Disclosure is highly recommended.")
        else:
            acceptance_file = os.path.realpath(os.path.join(references_dir, "acceptance-criteria.md"))
            if not os.path.isfile(acceptance_file):
                errors.append(f"Skill '{skill_name}' is missing `./acceptance-criteria.md`. All skills must have test criteria.")

        # Check for illegal root directories inside skill (enforce agentskills.io Optional Directories)
        allowed_skill_dirs = {".history", "scripts", "references", "assets", "examples", "templates", "evals", "tests"}
        for item in os.listdir(skill_path):
            full_item_path = os.path.join(skill_path, item)
            if os.path.isdir(full_item_path) and item not in allowed_skill_dirs and not item.startswith("."):
                errors.append(f"Skill '{skill_name}' contains illegal root directory '{item}/'. Only ['scripts', 'references', 'assets', 'examples', 'templates', 'evals', 'tests'] and specific scaffolds are allowed.")


def audit_plugin(plugin_path: str) -> bool:
    """Audit a plugin directory for Agent Skills Open Standard compliance."""
    print(f"Auditing Plugin at: {plugin_path}")
    plugin_name = os.path.basename(os.path.normpath(plugin_path))

    if _is_deprecated_stub(plugin_path):
        print(f"\n✅ AUDIT PASSED - Deprecated stub (no skills, README marked DEPRECATED) ✅")
        print(f"\nInfo: '{plugin_name}' is a deprecated stub and was skipped for full compliance checks.")
        return True

    errors: list = []
    warnings: list = []
    _check_root_structure(plugin_path, errors, warnings)
    _check_skills(plugin_path, errors, warnings)

    if errors:
        print("\n❌ AUDIT FAILED ❌")
        for e in errors:
            print(f"  - {e}")
    else:
        print("\n✅ AUDIT PASSED - Fully Open Standard Compliant ✅")

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  - {w}")

    return len(errors) == 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit a plugin for agent ecosystem standard compliance.")
    parser.add_argument("--path", required=True, help="Path to the plugin directory to audit")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.path):
        print(f"Error: Path '{args.path}' does not exist or is not a directory.")
        exit(1)
        
    success = audit_plugin(args.path)
    if not success:
        exit(1)
