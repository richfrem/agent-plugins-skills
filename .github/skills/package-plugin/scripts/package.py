#!/usr/bin/env python3
"""
package.py (CLI)
================
Purpose:
    Package a plugin directory into a distributable ZIP archive with correct
    flags for symlink preservation and artifact exclusion.

Usage:
    python3 package.py --plugin <path> [--output <dir>] [--validate-only] [--verify <zip>]

Output:
    <plugin-name>-v<version>.zip at the specified output directory.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile


# Patterns to exclude from the archive
EXCLUDE_PATTERNS = [
    ".DS_Store",
    "__pycache__",
    ".history",
    "node_modules",
    "*.pyc",
    ".git",
    "*.egg-info",
    ".pytest_cache",
]


def validate_manifest(plugin_path: str) -> dict:
    """Validate plugin.json and return the parsed manifest."""
    manifest_path = os.path.join(plugin_path, ".claude-plugin", "plugin.json")

    if not os.path.exists(manifest_path):
        print(f"ERROR: No .claude-plugin/plugin.json found at {plugin_path}")
        sys.exit(1)

    with open(manifest_path, "r") as f:
        try:
            manifest = json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in plugin.json: {e}")
            sys.exit(1)

    errors: list[str] = []

    # Check name
    name = manifest.get("name")
    if not name:
        errors.append("Missing required field: name")
    elif not re.match(r"^[a-z0-9-]+$", name):
        errors.append(f"name '{name}' must be kebab-case (lowercase, hyphens, no spaces)")

    # Check version is semver
    version = manifest.get("version")
    if version and not re.match(r"^\d+\.\d+\.\d+", version):
        errors.append(f"version '{version}' should be semver (e.g., 0.1.0)")

    # Check author is object
    author = manifest.get("author")
    if author and isinstance(author, str):
        errors.append("author must be an object {'name': '...'}, not a string")

    # Check for forbidden fields
    if "author" in manifest and isinstance(manifest["author"], dict):
        if "url" in manifest["author"]:
            errors.append("author.url is not in the spec - remove it")

    for forbidden in ["commands_dir", "skills_dir", "skills", "scripts", "dependencies"]:
        if forbidden in manifest:
            errors.append(f"'{forbidden}' is not in the spec - remove it (auto-discovered)")

    # Check at least one skill exists
    skills_dir = os.path.join(plugin_path, "skills")
    if os.path.exists(skills_dir):
        skill_count = sum(
            1 for d in os.listdir(skills_dir)
            if os.path.isfile(os.path.join(skills_dir, d, "SKILL.md"))
        )
        if skill_count == 0:
            errors.append("No skills/*/SKILL.md found - plugin has no skills")
    else:
        errors.append("No skills/ directory found")

    if errors:
        print(f"VALIDATION FAILED for {plugin_path}:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"VALID: {name} v{version or 'unversioned'} ({manifest.get('description', 'no description')[:60]})")
    return manifest


def package_plugin(plugin_path: str, output_dir: str) -> str:
    """Package the plugin into a ZIP archive."""
    manifest = validate_manifest(plugin_path)
    name = manifest["name"]
    version = manifest.get("version", "0.0.0")
    zip_name = f"{name}-v{version}.zip"
    zip_path = os.path.join(output_dir, zip_name)

    # Remove existing zip if present
    if os.path.exists(zip_path):
        os.remove(zip_path)

    # Build exclude args for zip command
    exclude_args = []
    for pattern in EXCLUDE_PATTERNS:
        exclude_args.extend(["-x", f"*/{pattern}/*", "-x", f"*/{pattern}"])

    # Zip with top-level wrapper directory (Claude expects this)
    parent_dir = os.path.dirname(os.path.abspath(plugin_path))
    plugin_dir_name = os.path.basename(os.path.abspath(plugin_path))

    cmd = [
        "zip", "-r",
        os.path.abspath(zip_path),
        plugin_dir_name,
    ] + exclude_args

    result = subprocess.run(cmd, cwd=parent_dir, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: zip failed:\n{result.stderr}")
        sys.exit(1)

    size_kb = os.path.getsize(zip_path) / 1024
    print(f"PACKAGED: {zip_path} ({size_kb:.1f} KB)")
    return zip_path


def package_skill(plugin_path: str, skill_name: str, output_dir: str) -> str:
    """Package a single skill from a plugin into its own ZIP (one SKILL.md per ZIP)."""
    skill_path = os.path.join(plugin_path, "skills", skill_name)

    if not os.path.exists(skill_path):
        print(f"ERROR: Skill not found: {skill_path}")
        sys.exit(1)

    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md):
        print(f"ERROR: No SKILL.md found in {skill_path}")
        sys.exit(1)

    zip_name = f"{skill_name}.zip"
    zip_path = os.path.join(output_dir, zip_name)

    if os.path.exists(zip_path):
        os.remove(zip_path)

    exclude_args = []
    for pattern in EXCLUDE_PATTERNS:
        exclude_args.extend(["-x", f"*/{pattern}/*", "-x", f"*/{pattern}"])

    # Zip with skill directory as wrapper (skill-name/SKILL.md at root)
    skills_dir = os.path.join(os.path.abspath(plugin_path), "skills")

    cmd = [
        "zip", "-r",
        os.path.abspath(zip_path),
        skill_name,
    ] + exclude_args

    result = subprocess.run(cmd, cwd=skills_dir, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: zip failed:\n{result.stderr}")
        sys.exit(1)

    size_kb = os.path.getsize(zip_path) / 1024
    print(f"PACKAGED SKILL: {zip_path} ({size_kb:.1f} KB)")
    return zip_path


def verify_package(zip_path: str) -> None:
    """Extract and verify a plugin ZIP archive."""
    if not os.path.exists(zip_path):
        print(f"ERROR: File not found: {zip_path}")
        sys.exit(1)

    verify_dir = os.path.join(tempfile.gettempdir(), "package-verify")
    if os.path.exists(verify_dir):
        shutil.rmtree(verify_dir)
    os.makedirs(verify_dir)

    # Extract
    result = subprocess.run(
        ["unzip", "-o", os.path.abspath(zip_path), "-d", verify_dir],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"ERROR: unzip failed:\n{result.stderr}")
        sys.exit(1)

    # Find the plugin root (first directory in extract)
    extracted = os.listdir(verify_dir)
    if not extracted:
        print("ERROR: ZIP was empty")
        sys.exit(1)

    plugin_root = os.path.join(verify_dir, extracted[0])

    # Check if this is a single skill or a full plugin
    if os.path.isfile(os.path.join(plugin_root, "SKILL.md")):
        print(f"VERIFIED SKILL: {extracted[0]} (single skill package)")
    else:
        manifest = validate_manifest(plugin_root)
        skills_dir = os.path.join(plugin_root, "skills")
        agents_dir = os.path.join(plugin_root, "agents")
        commands_dir = os.path.join(plugin_root, "commands")

        skill_count = 0
        if os.path.exists(skills_dir):
            skill_count = sum(
                1 for d in os.listdir(skills_dir)
                if os.path.isdir(os.path.join(skills_dir, d))
            )

        agent_count = 0
        if os.path.exists(agents_dir):
            agent_count = len(os.listdir(agents_dir))

        cmd_count = 0
        if os.path.exists(commands_dir):
            cmd_count = len(os.listdir(commands_dir))

        print(f"VERIFIED: {manifest['name']} - {skill_count} skills, {agent_count} agents, {cmd_count} commands")

    # Cleanup
    shutil.rmtree(verify_dir)


def main():
    parser = argparse.ArgumentParser(description="Package a plugin for distribution")
    parser.add_argument("--plugin", help="Path to the plugin directory to package")
    parser.add_argument("--skill", help="Package a single skill by name (requires --plugin)")
    parser.add_argument("--output", default=os.path.expanduser("~/Desktop"), help="Output directory (default: ~/Desktop)")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, don't package")
    parser.add_argument("--verify", help="Verify an existing ZIP archive")

    args = parser.parse_args()

    if args.verify:
        verify_package(args.verify)
    elif args.plugin:
        if args.validate_only:
            validate_manifest(args.plugin)
        elif args.skill:
            package_skill(args.plugin, args.skill, args.output)
        else:
            package_plugin(args.plugin, args.output)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
