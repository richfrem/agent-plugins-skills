#!/usr/bin/env python
"""
scaffold_apm.py (CLI)
=====================================

Purpose:
    Scaffolds a new APM-native package with standard directory structure, 
    manifest, and governance documentation.

Key Input Dependencies:
    - PyYAML                    — Used for serializing apm.yml package manifests
    - re, argparse, pathlib     — Standard library packages for CLI parsing and path validation

Layer: Codify / Scaffolding

Usage Examples:
    python scaffold_apm.py --name my-package --path ./packages --governance team

CLI Arguments:
    --name: Name of the package (kebab-case)
    --path: Destination parent directory
    --description: Optional description
    --version: Package version (default: 1.0.0)
    --author: Package author
    --governance: Governance lane (experimental, team, enterprise)
    --targets: Comma-separated list of targets (copilot, claude, cursor, etc.)
    --allow-hybrid: Allow scaffolding into an existing plugin directory
    --dry-run: Preview changes without writing to disk

Input Files:
    - None (scaffold-only)

Output:
    - apm.yml manifest
    - .apm/ source tree
    - docs/ governance, attribution, and lifecycle files
    - .gitignore (lockfile permitted)

Key Functions:
    - create_apm_package(): Primary logic for directory and file creation
"""

import argparse
import os
import yaml
import re
import sys
from pathlib import Path
from datetime import datetime

# Windows encoding safety
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, Exception):
        pass

def is_valid_name(name: str) -> bool:
    """Validates that the package name is kebab-case."""
    return bool(re.match(r'^[a-z0-9-]+$', name))

def generate_governance_doc(lane: str, package_name: str) -> str:
    """Returns the content for docs/governance.md."""
    return f"""# Governance: {package_name}

This package uses APM as its primary governance and distribution layer.

## Packaging Mode
Mode: APM-Native

## Governance Lane
Lane: {lane}

## Review Requirements
- **Experimental**: Local use only; no sensitive data or production systems.
- **Team**: Peer review, README, and acceptance criteria required.
- **Enterprise**: Security/privacy/dependency review and full validation report required.

## Promotion Rule
Governance controls promotion and distribution. This package is managed as an auditable enterprise asset.
"""

def generate_policy_doc(package_name: str) -> str:
    """Returns a starter apm-policy.yml for enterprise lane."""
    return f"""# APM Enterprise Policy: {package_name}
allowed_sources:
  - internal-registry.company.com
  - github.com/my-org/
blocked_patterns:
  - "**/secrets.json"
  - "**/*.env"
review_required:
  primitive_types: [agent, hook, mcp]
  risk_classification: medium
"""

def _validate_preconditions(name: str, package_root: Path, allow_hybrid: bool, dry_run: bool) -> None:
    """Validate name format and directory preconditions before scaffolding."""
    if not is_valid_name(name):
        print(f"❌ Error: Package name '{name}' must be kebab-case.")
        sys.exit(1)
    is_existing_plugin = (package_root / ".claude-plugin" / "plugin.json").exists()
    if is_existing_plugin and not allow_hybrid:
        print(f"❌ Error: Target '{package_root}' appears to be an existing plugin.")
        print("Use '/convert-plugin-to-apm' overlay mode or pass --allow-hybrid explicitly.")
        sys.exit(1)
    if not dry_run and package_root.exists() and not allow_hybrid:
        print(f"⚠️  Warning: Target directory '{package_root}' already exists. Refusing to overwrite.")
        sys.exit(1)


def _build_package_structure(name: str, package_root: Path, description: str, version: str,
                              author: str, governance: str, targets: str) -> dict:
    """Build the directory and file structure dict for the APM package."""
    apm_dir = package_root / ".apm"
    files = {
        package_root / "apm.yml": {
            "name": name, "version": version,
            "description": description or f"APM package for {name}",
            "author": author,
            "targets": [t.strip() for t in targets.split(',')],
            "dependencies": {"apm": [], "mcp": []},
            "includes": "auto",
            "metadata": {"governance_lane": governance, "generated_at": datetime.now().isoformat()}
        },
        package_root / ".gitignore": "apm_modules/\n.agents/\n.github/\n.claude/\n.cursor/\n.gemini/\n.codex/\n.windsurf/\n.opencode/\n# Commit apm.lock.yaml for reproducibility\n",
        package_root / "README.md": f"# {name}\n\n{description or f'APM package for {name}'}\n\n## APM Structure\nThis is an APM-native package. Primitives (skills, agents, prompts) are authored in the `.apm/` directory.\n",
        package_root / "docs" / "governance.md": generate_governance_doc(governance, name),
        package_root / "docs" / "attribution.md": f"# Attribution\n\nAuthor: {author}\nCreated: {datetime.now().strftime('%Y-%m-%d')}\n",
        package_root / "docs" / "package-lifecycle.md": "# Package Lifecycle\n\n1. Scaffold or convert package.\n2. Author primitives in `.apm/` or preserve plugin-native primitives in overlay mode.\n3. Validate package using `validate_apm_package.py`.\n4. Install package into runtime target directories using `apm install`.\n5. Compile top-level context files only when needed by the target harness (Gemini/Codex).\n6. Pack for distribution if needed.\n7. Publish/share.\n",
    }
    if governance == "enterprise":
        files[package_root / "apm-policy.yml"] = generate_policy_doc(name)
    dirs = [apm_dir / d for d in ("skills", "agents", "instructions", "prompts", "hooks", "mcp", "scripts", "tests")]
    dirs += [package_root / d for d in ("docs", "scripts", "tests")]
    return {"dirs": dirs, "files": files}


def _execute_scaffold(structure: dict, name: str, package_root: Path, governance: str,
                      allow_hybrid: bool, dry_run: bool) -> None:
    """Write directories and files from the structure dict, or print dry-run preview."""
    if dry_run:
        print("\n--- DRY RUN ---")
        for d in structure["dirs"]:
            print(f"[DIR]  {d}")
        for f in structure["files"]:
            print(f"[FILE] {f}")
        return
    for d in structure["dirs"]:
        d.mkdir(parents=True, exist_ok=True)
    for f_path, content in structure["files"].items():
        with open(f_path, "w", encoding="utf-8") as f:
            if isinstance(content, dict):
                yaml.dump(content, f, sort_keys=False)
            else:
                f.write(content)
    print(f"\n# APM Scaffold Report")
    print(f"Mode: {'Hybrid' if allow_hybrid else 'New-Package'}")
    print(f"Governance Lane: {governance}")
    print(f"Files Created: {len(structure['files'])}")
    print(f"Validation Command: python scripts/validate_apm_package.py --path {package_root}")
    print(f"Recommended Next: /create-skill inside {name}")


def create_apm_package(
    name: str,
    path: str,
    description: str = "",
    version: str = "1.0.0",
    author: str = "Generated via Agent Scaffolder",
    governance: str = "experimental",
    targets: str = "copilot,claude,cursor",
    allow_hybrid: bool = False,
    dry_run: bool = False,
) -> None:
    """Scaffolds a new APM package structure."""
    package_root = Path(path) / name
    _validate_preconditions(name, package_root, allow_hybrid, dry_run)
    print(f"🏗️  Planning scaffolding for APM package '{name}'...")
    structure = _build_package_structure(name, package_root, description, version, author, governance, targets)
    _execute_scaffold(structure, name, package_root, governance, allow_hybrid, dry_run)

def main():
    """CLI entry point: parses configuration arguments and triggers APM package scaffolding."""
    parser = argparse.ArgumentParser(description="APM Package Scaffolder")
    parser.add_argument("--name", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--description", default="")
    parser.add_argument("--version", default="1.0.0")
    parser.add_argument("--author", default="Generated via Agent Scaffolder")
    parser.add_argument("--governance", default="experimental", choices=["experimental", "team", "enterprise"])
    parser.add_argument("--targets", default="copilot,claude,cursor")
    parser.add_argument("--allow-hybrid", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    
    args = parser.parse_args()
    create_apm_package(**vars(args))

if __name__ == "__main__":
    main()
