#!/usr/bin/env python
"""
validate_apm_package.py (CLI)
=====================================

Purpose:
    Performs deterministic validation of an APM package.
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

def validate_package(path: str, as_json: bool = False) -> bool:
    root = Path(path).resolve()
    if not root.exists():
        if not as_json: print(f"❌ Error: Path '{root}' does not exist.")
        return False

    issues, warnings = [], []
    manifest = {}
    
    # 1. Manifest & Basic Schema
    manifest_path = root / "apm.yml"
    if not manifest_path.exists():
        issues.append("MISSING: apm.yml is required.")
    else:
        try:
            with open(manifest_path, "r", encoding='utf-8') as f: manifest = yaml.safe_load(f) or {}
            name = manifest.get("name", "")
            version = manifest.get("version", "")
            
            # Kebab-case name (Priority 6)
            if name and not re.match(r'^[a-z0-9-]+$', name):
                issues.append(f"SCHEMA: Name '{name}' must be kebab-case.")
            
            # Semver-like version (Priority 6)
            if version and not re.match(r'^\d+\.\d+\.\d+', str(version)):
                warnings.append(f"SCHEMA: Version '{version}' should follow semver (x.y.z).")

            if not name: issues.append("SCHEMA: 'name' is required.")
            if not version: issues.append("SCHEMA: 'version' is required.")
        except Exception as e: issues.append(f"PARSE: {e}")

    metadata = manifest.get("metadata", {})
    mode = metadata.get("packaging_mode", "unknown")
    lane = metadata.get("governance_lane", "unknown")
    has_apm = (root / ".apm").exists()

    # 2. Structure & Primitives
    if mode == "full":
        if not has_apm: issues.append("STRUCTURE: Full mode requires .apm/ directory.")
        for folder in ["skills", "agents", "prompts", "hooks"]:
            if (root / folder).exists() and (root / ".apm" / folder).exists():
                issues.append(f"STRUCTURE: Duplicate primitive root '{folder}/' found outside .apm/ in Full mode.")
    elif mode == "hybrid":
        if not has_apm: warnings.append("STRUCTURE: Hybrid mode normally includes a .apm/ directory.")

    # 3. Specific Primitives
    if has_apm:
        # Hooks check (Priority 7)
        if (root / ".apm" / "hooks").exists():
            if not list((root / ".apm" / "hooks").glob("*.json")):
                warnings.append("PRIMITIVES: .apm/hooks/ exists but contains no .json files.")
        
        # Prompts check (Priority 6)
        if (root / ".apm" / "prompts").exists():
            generic_md = [f.name for f in (root / ".apm" / "prompts").glob("*.md") if not f.name.endswith(".prompt.md")]
            if generic_md:
                warnings.append(f"PRIMITIVES: .apm/prompts/ contains generic .md files: {generic_md}. Rename to .prompt.md for APM compatibility.")

    # 4. Governance & Docs
    if lane == "enterprise":
        policy_path = root / "apm-policy.yml"
        if not policy_path.exists():
            warnings.append("GOVERNANCE: Enterprise lane recommends an apm-policy.yml.")
        else:
            with open(policy_path, "r", encoding='utf-8') as f: policy_content = f.read()
            if "company.com" in policy_content or "my-org" in policy_content:
                warnings.append("GOVERNANCE: apm-policy.yml appears to contain template placeholders.")

    if not (root / "README.md").exists(): warnings.append("DOCS: Missing README.md.")

    result = {
        "path": str(root), "passed": len(issues) == 0, "issues": issues, "warnings": warnings,
        "mode": mode, "governance_lane": lane
    }

    if as_json: print(json.dumps(result, indent=2))
    else:
        print(f"🔍 Auditing: {root.name}\n" + "-"*40)
        for i in issues: print(f"❌ {i}")
        for w in warnings: print(f"⚠️  {w}")
        print("-"*40)
        print("✅ VALIDATION PASSED" if result["passed"] else f"❌ VALIDATION FAILED")

    return result["passed"]

def main():
    parser = argparse.ArgumentParser(description="APM Package Validator")
    parser.add_argument("--path", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    sys.exit(0 if validate_package(args.path, args.json) else 1)

if __name__ == "__main__": main()
