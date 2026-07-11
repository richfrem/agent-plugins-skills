#!/usr/bin/env python
"""
migrate_to_apm.py (CLI)
=====================================

Purpose:
    Analyzes an existing Claude plugin and implements an APM integration path
    (Overlay, Hybrid, or Full).

Key Input Dependencies:
    - Existing Claude plugin directory structure (plugin.json, skills/, agents/, etc.)
    - PyYAML for configuration file generation
    - pathlib.Path for directory traversal
    - shutil for directory operations

Layer: Codify / Migration
"""

import argparse
import os
import json
import yaml
import shutil
import sys
import re
from pathlib import Path
from datetime import datetime

# Windows encoding safety
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, Exception): pass

def generate_governance_doc(mode: str, lane: str, package_name: str) -> str:
    """Generate governance documentation based on migration mode (full, hybrid, overlay)."""
    if mode == "full":
        return (f"# Governance: {package_name}\nMode: {mode}\nLane: {lane}\n\n"
                f"## Principle\nThis package has been converted to an APM-native layout. "
                f"The `.apm/` directory is the canonical source tree for APM-managed primitives. "
                f"The original plugin source remains preserved outside this converted package and "
                f"should not be modified by this conversion.\n")
    elif mode == "hybrid":
        return (f"# Governance: {package_name}\nMode: {mode}\nLane: {lane}\n\n"
                f"## Principle\nPlugin-native primitives remain in place. `.apm/` is used for "
                f"new APM-native governance assets or future primitives.\n")
    else: # overlay
        return (f"# Governance: {package_name}\nMode: {mode}\nLane: {lane}\n\n"
                f"## Principle\nThe plugin remains the source package. APM adds governance, "
                f"manifest, lockfile, audit, and distribution metadata.\n")

def generate_policy_doc(package_name: str) -> str:
    """Generate APM enterprise policy template with allowed sources and review requirements."""
    return f"# APM Enterprise Policy: {package_name}\n# TEMPLATE ONLY: replace allowed_sources before enterprise use.\nallowed_sources: [\"internal-registry.company.com\"]\nreview_required:\n  primitive_types: [agent, hook, mcp]\n  risk_classification: medium\n"

def dereference_content(path: Path) -> str:
    """Reads content, following relative path pointers if found."""
    if not path.exists(): return ""
    with open(path, "r", encoding='utf-8') as f:
        content = f.read().strip()
    
    # Simple heuristic: if content is a single line starting with ../ or ./, it's a pointer
    if content.count('\n') == 0 and (content.startswith("../") or content.startswith("./")):
        ptr_path = (path.parent / content).resolve()
        if ptr_path.exists() and ptr_path.is_file():
            with open(ptr_path, "r", encoding='utf-8') as f: return f.read()
    
    with open(path, "r", encoding='utf-8') as f: return f.read()

def migrate_to_apm(
    source_path: str,
    output_path: str = None,
    output_exact: str = None,
    mode: str = "overlay",
    governance: str = "experimental",
    dry_run: bool = False,
    output_name: str = None
) -> None:
    """Migrate Claude plugin to APM format with specified mode (overlay/hybrid/full)."""
    source = Path(source_path).resolve()
    if not source.exists():
        print(f"❌ Error: Source path '{source}' does not exist."); sys.exit(1)

    # Metadata discovery
    manifest_path = source / ".claude-plugin" / "plugin.json"
    plugin_data = {}
    if manifest_path.exists():
        with open(manifest_path, "r", encoding='utf-8') as f: plugin_data = json.load(f)
    
    name = plugin_data.get("name", source.name)
    version = plugin_data.get("version", "1.0.0")
    description = plugin_data.get("description", f"Migrated APM {mode} for {name}")
    author = plugin_data.get("author", {}).get("name", "Unknown") if isinstance(plugin_data.get("author"), dict) else plugin_data.get("author", "Unknown")

    if mode == "full":
        if output_exact:
            dest_root = Path(output_exact).resolve()
        elif output_path:
            target_name = output_name if output_name else name
            dest_root = Path(output_path).resolve() / target_name
        else:
            print("❌ Error: --output or --output-exact required for 'full' mode."); sys.exit(1)
        
        if dest_root.exists() and not dry_run:
            print(f"❌ Error: Output path '{dest_root}' already exists. Aborting."); sys.exit(1)
    else:
        dest_root = source

    plan = {"created": [], "copied": [], "converted": [], "warnings": [], "collisions": []}
    
    # 1. Plan Phase
    if mode == "full":
        dest_prompts = set()
        if (source / "prompts").exists():
            for p in (source / "prompts").glob("*.prompt.md"):
                dest_prompts.add(p.name)
                plan["copied"].append(f"prompts/{p.name}")
        
        if (source / "commands").exists():
            for cmd in (source / "commands").glob("*.md"):
                normalized = f"{cmd.stem}.prompt.md"
                if normalized in dest_prompts:
                    plan["collisions"].append(f"commands/{cmd.name} and prompts/ both map to .apm/prompts/{normalized}")
                dest_prompts.add(normalized)
                plan["converted"].append(f"commands/{cmd.name} -> .apm/prompts/{normalized}")

        for folder in ["skills", "agents", "hooks", "instructions"]:
            if (source / folder).exists():
                plan["copied"].append(f"{folder}/")

        for mcp in [".mcp.json", "mcp-servers.json", "mcp.json"]:
            if (source / mcp).exists():
                plan["copied"].append(f"{mcp}")

    # Heuristic: Check for potential script path issues
    for skill_dir in (source / "skills").glob("*"):
        if (skill_dir / "scripts").exists():
            for script in (skill_dir / "scripts").glob("*.py"):
                with open(script, "r", encoding='utf-8', errors='ignore') as f:
                    script_content = f.read()
                    if 'resources' in script_content and 'assets' not in script_content:
                        plan["warnings"].append(f"Script {script.relative_to(source)} contains 'resources' but no 'assets' fallback.")

    # CRITICAL: Abort on collision (Priority 1)
    if plan["collisions"]:
        print(f"❌ Collisions detected in migration plan:")
        for c in plan["collisions"]: print(f"  - {c}")
        if not dry_run: sys.exit(1)

    if dry_run:
        print(f"\n--- DRY RUN: {mode.upper()} ---")
        print(f"Source: {source}")
        print(f"Dest:   {dest_root}")
        print(f"Lane:   {governance}")
        print(f"Metadata Source: {'.claude-plugin/plugin.json' if manifest_path.exists() else 'Folder name'}")
        
        if mode == "full":
            print(f"Plan: {len(plan['copied'])} items to copy, {len(plan['converted'])} commands to convert.")
            for c in plan["copied"]: print(f"  [COPY] {c}")
            for c in plan["converted"]: print(f"  [CONV] {c}")
        if plan["warnings"]:
            print(f"Warnings: {len(plan['warnings'])}")
            for w in plan["warnings"]: print(f"  [WARN] {w}")
        return

    # 2. Execution Logic
    dest_root.mkdir(parents=True, exist_ok=True)
    apm_dir = dest_root / ".apm"
    
    if mode == "full":
        apm_dir.mkdir(exist_ok=True)
        for folder in ["skills", "agents", "hooks", "instructions"]:
            if (source / folder).exists():
                shutil.copytree(source / folder, apm_dir / folder, dirs_exist_ok=True)

        (apm_dir / "prompts").mkdir(exist_ok=True)
        if (source / "prompts").exists():
            for p in (source / "prompts").glob("*.prompt.md"): 
                shutil.copy2(p, apm_dir / "prompts" / p.name)
        
        if (source / "commands").exists():
            for cmd in (source / "commands").glob("*.md"):
                dst_file = apm_dir / "prompts" / f"{cmd.stem}.prompt.md"
                with open(cmd, "r", encoding='utf-8') as f: content = f.read()
                with open(dst_file, "w", encoding='utf-8') as f:
                    f.write(f"<!-- Migrated from plugin command: {cmd.name} -->\n" + content)

        for mcp in [".mcp.json", "mcp-servers.json", "mcp.json"]:
            if (source / mcp).exists():
                (apm_dir / "mcp").mkdir(exist_ok=True)
                shutil.copy2(source / mcp, apm_dir / "mcp" / mcp)

        # Dereference requirements files in full mode
        for req_file in apm_dir.rglob("requirements.*"):
            if req_file.is_file():
                with open(req_file, "r", encoding='utf-8') as f:
                    raw_content = f.read().strip()
                
                # If it's a relative pointer (../ or ./), resolve against SOURCE
                if raw_content.count('\n') == 0 and (raw_content.startswith("../") or raw_content.startswith("./")):
                    # Calculate where it would have pointed in the SOURCE tree
                    rel_to_apm = req_file.relative_to(apm_dir)
                    source_file_loc = source / rel_to_apm
                    actual_ptr_target = (source_file_loc.parent / raw_content).resolve()
                    
                    if actual_ptr_target.exists() and actual_ptr_target.is_file():
                        with open(actual_ptr_target, "r", encoding='utf-8') as f:
                            final_content = f.read()
                        with open(req_file, "w", encoding='utf-8') as f:
                            f.write(final_content)

        # README Banner
        readme_path = source / "README.md"
        if readme_path.exists():
            with open(readme_path, "r", encoding='utf-8') as f: original_readme = f.read()
            banner = ("> [!NOTE]\n"
                     "> This package was converted from a Claude plugin into an APM-native package.\n"
                     "> APM-managed source primitives now live under `.apm/`.\n"
                     "> The original plugin README below is preserved for historical context.\n\n---\n\n")
            with open(dest_root / "README.md", "w", encoding='utf-8') as f:
                f.write(banner + original_readme)
        else:
            with open(dest_root / "README.md", "w", encoding='utf-8') as f:
                f.write(f"# {name}\n\nMigrated from {source}\nMode: {mode}\nLane: {governance}\n")
    
    elif mode == "hybrid":
        apm_dir.mkdir(parents=True, exist_ok=True)
        (apm_dir / "prompts").mkdir(exist_ok=True)
        (apm_dir / "instructions").mkdir(exist_ok=True)
        with open(apm_dir / "README.md", "w", encoding='utf-8') as f:
            f.write(f"# APM Governance Layer\nThis directory stores APM governance assets for the {name} hybrid package.\n")
        plan["created"].append(".apm/")

    # 3. Final Assets
    manifest = {
        "name": name, "version": version, "description": description, "author": author,
        "targets": ["copilot", "claude", "cursor"],
        "includes": "auto",
        "metadata": {
            "packaging_mode": mode, "governance_lane": governance,
            "source_layout": "claude-plugin" if manifest_path.exists() else "unknown",
            "source_plugin_manifest": str(manifest_path) if manifest_path.exists() else None,
            "generated_at": datetime.now().isoformat()
        }
    }
    with open(dest_root / "apm.yml", "w", encoding='utf-8') as f: yaml.dump(manifest, f, sort_keys=False)
    
    # Optional Snapshot
    if manifest_path.exists() and mode == "full":
        (dest_root / "docs" / "source-plugin").mkdir(parents=True, exist_ok=True)
        shutil.copy2(manifest_path, dest_root / "docs" / "source-plugin" / "plugin.json")

    docs_dir = dest_root / "docs"
    docs_dir.mkdir(exist_ok=True)
    with open(docs_dir / "governance.md", "w", encoding='utf-8') as f: f.write(generate_governance_doc(mode, governance, name))
    
    policy_gen = False
    if governance == "enterprise":
        with open(dest_root / "apm-policy.yml", "w", encoding='utf-8') as f: f.write(generate_policy_doc(name))
        policy_gen = True

    with open(docs_dir / "migration-notes.md", "w", encoding='utf-8') as f:
        f.write(f"# Migration Notes\nSource: {source}\nDest: {dest_root}\nMode: {mode}\nLane: {governance}\n\n")
        f.write(f"## Evidence\n- Dry run performed: {'Yes' if dry_run else 'No'}\n")
        f.write(f"- Requested output: {output_exact or output_path or 'Source dir'}\n")
        f.write(f"- Actual output: {dest_root}\n\n")
        f.write(f"## Metadata Source\n{'.claude-plugin/plugin.json' if manifest_path.exists() else 'Folder name'}\n\n")
        f.write(f"## Copied Primitives\n" + "\n".join(plan["copied"]) + "\n\n")
        f.write(f"## Converted Commands\n" + "\n".join(plan["converted"]) + "\n\n")
        if plan["warnings"]:
            f.write(f"## Heuristic Warnings (Review Required)\n" + "\n".join(plan["warnings"]) + "\n\n")
        f.write(f"## Enterprise Policy Generated\n{'Yes' if policy_gen else 'No'}\n\n")
        f.write(f"## Collision Status\n{'No collisions detected' if not plan['collisions'] else 'Collisions resolved during planning'}\n\n")
        f.write(f"## Validation\nRun: python scripts/validate_apm_package.py --path {dest_root}\n")
        f.write(f"## Recommended Next Step\n/os-loop or manual primitive authoring in .apm/\n")

    print(f"✅ Migration complete! Result at {dest_root}")

def main() -> None:
    """Parse CLI arguments and migrate Claude plugin to APM format."""
    parser = argparse.ArgumentParser(description="Plugin to APM Migrator")
    parser.add_argument("--source-path", required=True, dest="source_path")
    parser.add_argument("--output", dest="output_path")
    parser.add_argument("--output-exact", dest="output_exact", help="Unambiguous destination path")
    parser.add_argument("--output-name", dest="output_name")
    parser.add_argument("--mode", default="overlay", choices=["overlay", "hybrid", "full"])
    parser.add_argument("--governance", default="experimental", choices=["experimental", "team", "enterprise"])
    parser.add_argument("--dry-run", action="store_true")
    migrate_to_apm(**vars(parser.parse_args()))

if __name__ == "__main__": main()
