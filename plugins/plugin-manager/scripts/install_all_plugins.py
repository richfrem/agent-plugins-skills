"""
Install All Plugins (CLI)
=========================

Purpose:
    Iterates through all directories in `plugins/` and runs the `bridge_installer.py` for each one 
    to orchestrate a bulk repository update, strictly using the new .agents centralized symlink pattern.

Layer: Plugin Manager / Installation

Usage Examples:
    python3 plugins/plugin-manager/scripts/install_all_plugins.py
    python3 plugins/plugin-manager/scripts/install_all_plugins.py --plugins-dir "temp/agent-plugins-skills/plugins"

Supported Object Types:
    - None (Batch execution)

CLI Arguments:
    --dry-run: Pass --dry-run to each bridge_installer invocation.
    --plugins-dir: Optional path to a specific plugins folder to install from.

Input Files:
    - bridge_installer.py (Subprocess script)

Output:
    - Updates local agent environments and skills-lock.json.

Key Functions:
    _compute_folder_hash(): Computes simple SHA-256 over relative files.
    _update_lock_hashes(): Backfills hashes in skills-lock.json.

Script Dependencies:
    os, sys, argparse, subprocess, shutil, json, hashlib, pathlib

Consumed by:
    - None (Standalone script)
Related:
    - scripts/bridge_installer.py
"""
import os
import sys
import argparse

# Force UTF-8 output on Windows to avoid UnicodeEncodeError with emoji in print()
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import subprocess
import shutil
import json
import hashlib
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent 
PLUGINS_ROOT = PROJECT_ROOT / "plugins"

INSTALLER_SCRIPT = SCRIPT_DIR / "bridge_installer.py"

def _compute_folder_hash(folder: Path) -> str:
    """Matches npx skills computeSkillFolderHash simple SHA-256 over relative files."""
    hasher = hashlib.sha256()
    file_list = []
    
    for root_dir, dirs, files in os.walk(folder):
        # Skip hidden dirs and known noise
        dirs[:] = [d for d in dirs if not d.startswith('.') 
                   and d not in ('node_modules', '__pycache__')]
        for f in files:
            file_list.append(Path(root_dir) / f)
            
    # Sort files for deterministic hash
    file_list.sort(key=lambda p: str(p.relative_to(folder)))
    
    for f in file_list:
        try:
            rel_path = str(f.relative_to(folder)).replace('\\', '/')
            hasher.update(rel_path.encode("utf-8"))
            hasher.update(f.read_bytes())
        except Exception:
            pass
            
    return hasher.hexdigest()

def _update_lock_hashes(root: Path, plugins_root: Path, dry_run: bool = False) -> None:
    if dry_run:
        print("  [DRY RUN] Would backfill hashes in skills-lock.json")
        return
        
    lock_path = root / "skills-lock.json"
    if not lock_path.exists():
        return
        
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except Exception:
        return
        
    changed = False
    for skill_name, entry in lock.get("skills", {}).items():
        if entry.get("sourceType") == "local" and not entry.get("computedHash"):
            # Find the canonical skill dir
            skill_dir = root / ".agents" / "skills" / skill_name
            if skill_dir.exists():
                entry["computedHash"] = _compute_folder_hash(skill_dir)
                changed = True
                
    if changed:
        lock_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
        print("  ✓ Backfilled empty hashes in skills-lock.json")

def main() -> None:
    parser = argparse.ArgumentParser(description="Install all plugins via bridge_installer")
    parser.add_argument("--dry-run", action="store_true", help="Pass --dry-run to each bridge_installer invocation")
    parser.add_argument("--plugins-dir", type=str, help="Optional path to the plugins folder to install from (defaults to the project's plugins/ directory)")
    args = parser.parse_args()

    plugins_root = Path(args.plugins_dir).resolve() if args.plugins_dir else PLUGINS_ROOT
    if not plugins_root.exists() or not plugins_root.is_dir():
        print(f"❌ Error: Plugins source directory not found at {plugins_root}")
        sys.exit(1)

    tag = " [DRY RUN]" if args.dry_run else ""
    print(f"\n{'='*80}")
    print(f"Full-stack installer{tag}: deploys skills + commands + rules + hooks.")
    print("npx skills installs SKILLS ONLY. Use this script for complete deployment.")
    print(f"{'='*80}\n")

    if not INSTALLER_SCRIPT.exists():
        print(f"❌ Error: Installer script not found at {INSTALLER_SCRIPT}")
        sys.exit(1)

    print(f"🚀 Starting Local Batch Installation mimicking `npx skills add ./plugins/`...")
    print("Flushing old .agents/ source block to ensure a clean central repo before symlinking...")
    target_agents_repo = Path.cwd() / ".agents"
    if not args.dry_run:
        if target_agents_repo.exists():
            shutil.rmtree(target_agents_repo, ignore_errors=True)
    else:
        print("  [DRY RUN] Would delete .agents/")
    
    plugins_processed = 0
    plugins_failed = 0
    
    # Iterate over all directories in plugins/
    for plugin_dir in sorted(plugins_root.iterdir()):
        if not plugin_dir.is_dir():
            continue
            
        # Skip special directories
        if plugin_dir.name.startswith(".") or plugin_dir.name.startswith("__"):
            continue
        if plugin_dir.name in ["node_modules", "venv", "env"]:
            continue
            
        print(f"\n📦 Installing Component: {plugin_dir.name}")
        
        try:
            # We use subprocess to isolate execution and ensure clean state per plugin
            cmd = [
                sys.executable, 
                str(INSTALLER_SCRIPT),
                "--plugin", str(plugin_dir),
                # No --target: bridge_installer auto-detects from existing directories
            ]
            
            if args.dry_run:
                cmd.append("--dry-run")
            
            subprocess.run(cmd, check=True, text=True)
            plugins_processed += 1
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {plugin_dir.name}")
            plugins_failed += 1
        except Exception as e:
            print(f"❌ Unexpected error installing {plugin_dir.name}: {e}")
            plugins_failed += 1

    _update_lock_hashes(Path.cwd(), plugins_root, args.dry_run)

    print("\n" + "="*50)
    print(f"Batch Installation into .agents/ Complete")
    print(f"✅ Success: {plugins_processed}")
    if plugins_failed > 0:
        print(f"❌ Failed:  {plugins_failed}")
    print("="*50)

if __name__ == "__main__":
    main()
