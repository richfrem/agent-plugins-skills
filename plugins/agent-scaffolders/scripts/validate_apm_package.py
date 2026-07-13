#!/usr/bin/env python
"""
validate_apm_package.py (CLI)
=====================================

Purpose:
    Performs deterministic validation of an APM package.

Key Input Dependencies:
    - PyYAML                    — Used for parsing apm.yml package manifests and policy configurations
    - argparse, json, re, sys   — Standard library packages for CLI parsing, reporting, and name matching
"""

import argparse
import os
import yaml
import sys
import json
import re
from pathlib import Path

# Windows encoding safety
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, Exception): pass

def _check_manifest(root: Path, issues: list, warnings: list) -> dict:
    """Parse and validate apm.yml; return the manifest dict."""
    manifest: dict = {}
    manifest_path = root / "apm.yml"
    if not manifest_path.exists():
        issues.append("MISSING: apm.yml is required.")
        return manifest
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = yaml.safe_load(f) or {}
        name = manifest.get("name", "")
        version = manifest.get("version", "")
        if name and not re.match(r'^[a-z0-9-]+$', name):
            issues.append(f"SCHEMA: Name '{name}' must be kebab-case.")
        if version and not re.match(r'^\d+\.\d+\.\d+', str(version)):
            warnings.append(f"SCHEMA: Version '{version}' should follow semver (x.y.z).")
        if not name:
            issues.append("SCHEMA: 'name' is required.")
        if not version:
            issues.append("SCHEMA: 'version' is required.")
    except Exception as e:
        issues.append(f"PARSE: {e}")
    return manifest


def _check_structure(root: Path, manifest: dict, issues: list, warnings: list) -> bool:
    """Check .apm/ structure and primitive directories; return has_apm."""
    metadata = manifest.get("metadata", {})
    mode = metadata.get("packaging_mode", "unknown")
    has_apm = (root / ".apm").exists()
    if mode == "full":
        if not has_apm:
            issues.append("STRUCTURE: Full mode requires .apm/ directory.")
        for folder in ["skills", "agents", "prompts", "hooks"]:
            if (root / folder).exists() and (root / ".apm" / folder).exists():
                issues.append(f"STRUCTURE: Duplicate primitive root '{folder}/' found outside .apm/ in Full mode.")
    elif mode == "hybrid":
        if not has_apm:
            warnings.append("STRUCTURE: Hybrid mode normally includes a .apm/ directory.")
    if has_apm:
        hooks_dir = root / ".apm" / "hooks"
        if hooks_dir.exists() and not list(hooks_dir.glob("*.json")):
            warnings.append("PRIMITIVES: .apm/hooks/ exists but contains no .json files.")
        prompts_dir = root / ".apm" / "prompts"
        if prompts_dir.exists():
            generic_md = [f.name for f in prompts_dir.glob("*.md") if not f.name.endswith(".prompt.md")]
            if generic_md:
                warnings.append(f"PRIMITIVES: .apm/prompts/ contains generic .md files: {generic_md}.")
    return has_apm


def _check_governance(root: Path, manifest: dict, issues: list, warnings: list) -> None:
    """Check enterprise governance policy and README presence."""
    metadata = manifest.get("metadata", {})
    lane = metadata.get("governance_lane", "unknown")
    if lane == "enterprise":
        policy_path = root / "apm-policy.yml"
        if not policy_path.exists():
            warnings.append("GOVERNANCE: Enterprise lane recommends an apm-policy.yml.")
        else:
            with open(policy_path, "r", encoding="utf-8") as f:
                policy_content = f.read()
            if "company.com" in policy_content or "my-org" in policy_content:
                warnings.append("GOVERNANCE: apm-policy.yml appears to contain template placeholders.")
    if not (root / "README.md").exists():
        warnings.append("DOCS: Missing README.md.")


def _print_result(result: dict) -> None:
    """Print human-readable validation result to stdout."""
    root_name = Path(result["path"]).name
    print(f"\U0001f50d Auditing: {root_name}\n" + "-" * 40)
    for i in result["issues"]:
        print(f"\u274c {i}")
    for w in result["warnings"]:
        print(f"\u26a0\ufe0f  {w}")
    print("-" * 40)
    print("\u2705 VALIDATION PASSED" if result["passed"] else "\u274c VALIDATION FAILED")


def validate_package(path: str, as_json: bool = False) -> bool:
    """Deterministic validation of an APM package's directories, manifest, and governance policy."""
    root = Path(path).resolve()
    if not root.exists():
        if not as_json:
            print(f"\u274c Error: Path '{root}' does not exist.")
        return False
    issues: list = []
    warnings: list = []
    manifest = _check_manifest(root, issues, warnings)
    _check_structure(root, manifest, issues, warnings)
    _check_governance(root, manifest, issues, warnings)
    metadata = manifest.get("metadata", {})
    result = {
        "path": str(root), "passed": len(issues) == 0,
        "issues": issues, "warnings": warnings,
        "mode": metadata.get("packaging_mode", "unknown"),
        "governance_lane": metadata.get("governance_lane", "unknown"),
    }
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        _print_result(result)
    return result["passed"]

def main():
    """CLI entry point: parses CLI arguments and runs the APM package validation."""
    parser = argparse.ArgumentParser(description="APM Package Validator")
    parser.add_argument("--path", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    sys.exit(0 if validate_package(args.path, args.json) else 1)

if __name__ == "__main__": main()
