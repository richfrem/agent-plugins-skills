"""
Sync Plugins with Inventory
===========================

Purpose:
    Synchronizes the agent environments with the local `plugins/` directory.
    Uses `plugin-sources.json` as the authoritative registry of installed plugins
    to safely identify and clean up deleted/removed plugins.

Layer: Plugin Manager / Synchronization

Usage Examples:
    python plugins/plugin-manager/scripts/sync_with_inventory.py [--dry-run]

Supported Object Types:
    - None (Synchronization)

CLI Arguments:
    --dry-run: Simulate cleanup without deleting.
    --cleanup-only: Run cleanup analysis only, skip installation.

Key Input Dependencies:
    plugin-sources.json         — authoritative registry of all installed plugins and their sources
    .agents/ownership/{name}.json — per-plugin artifact manifests used for precise cleanup
    skills-lock.json            — checked during validation for skill registration
    plugins/plugin-manager/scripts/plugin_installer.py — subprocess install engine
    plugins/plugin-manager/scripts/plugin_add.py — subprocess sync engine per source

Input Files:
    - plugin-sources.json (canonical install registry)
    - plugin_installer.py (subprocess installation engine)

Output:
    - Cleans or installs plugin artifacts on agent targets.

Key Functions:
    clean_plugin_artifacts(): Removes artifacts for a specific plugin.
    run_plugin_installer(): Runs plugin_installer for a plugin.
    get_installed_plugin_names(): Returns set of plugin names from plugin-sources.json.

Script Dependencies:
    os, sys, json, shutil, argparse, subprocess, pathlib

Consumed by:
    - None (Standalone script)
Related:
    - scripts/plugin_inventory.py
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path

# Removed plugin_inventory import as it is now obsolete.

# --- Configuration ---

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[2]  # scripts→plugin-manager→plugins→ROOT
PLUGIN_INSTALLER = PROJECT_ROOT / "plugins" / "plugin-manager" / "scripts" / "plugin_installer.py"

AGENT_DIRS = {
    "antigravity": {
        "dirs": [".agents/workflows", ".agents/skills", ".agents/rules"],
    },
    "github": {
        "dirs": [".github/prompts", ".github/skills", ".github/rules"],
    },
    "gemini": {
        "dirs": [".gemini/commands", ".gemini/skills", ".gemini/rules"],
    },
    "claude": {
        "dirs": [".claude/commands", ".claude/skills", ".claude/rules"],
    }
}

def clean_plugin_artifacts(plugin_name: str, root: Path, dry_run: bool) -> None:
    """Removes artifacts for a specific plugin from all agent directories."""
    print(f"  [CLEAN] Removing artifacts for '{plugin_name}'...")
    ownership_file = root / ".agents" / "ownership" / f"{plugin_name}.json"
    removed_count = 0
    
    if ownership_file.exists():
        print(f"    - Using ownership manifest: {ownership_file.relative_to(root)}")
        try:
            data = json.loads(ownership_file.read_text(encoding="utf-8"))
            artifacts = data.get("artifacts", [])
            for art_rel in sorted(artifacts, key=len, reverse=True):
                art_path = root / art_rel
                if art_path.exists():
                    print(f"    - Deleting owned artifact: {art_rel}")
                    if not dry_run:
                        if art_path.is_symlink() or (hasattr(os.path, 'isjunction') and os.path.isjunction(art_path)):
                            art_path.unlink()
                        elif art_path.is_dir():
                            shutil.rmtree(art_path)
                        else:
                            art_path.unlink()
                    removed_count += 1
            if not dry_run:
                ownership_file.unlink()
        except Exception as e:
            print(f"    Warning: Failed to clean via ownership manifest: {e}")
            
    if not ownership_file.exists() or removed_count == 0:
        for agent, config in AGENT_DIRS.items():
            for dir_path_str in config["dirs"]:
                target_dir = root / dir_path_str
                if not target_dir.exists():
                    continue
                    
                if dir_path_str.endswith("skills") or dir_path_str.endswith("rules"):
                    target_subdir = target_dir / plugin_name
                    if target_subdir.exists() and target_subdir.is_dir():
                        print(f"    - Deleting legacy dir: {target_subdir}")
                        if not dry_run:
                            shutil.rmtree(target_subdir)
                else:
                    for f in target_dir.iterdir():
                        if f.is_file() and f.name.startswith(f"{plugin_name}_"):
                            print(f"    - Deleting legacy file: {f}")
                            if not dry_run:
                                f.unlink()


def run_plugin_installer(plugin_path: Path) -> None:
    """Runs plugin_installer.py for a specific plugin."""
    cmd = [sys.executable, str(PLUGIN_INSTALLER), "--plugin", str(plugin_path)]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"  [INSTALL] Success: {plugin_path.name}")
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Failed to install {plugin_path.name}: {e.stderr.decode()}")


def get_installed_plugin_names(root: Path) -> set:
    """Returns the set of plugin names tracked in plugin-sources.json.

    Supports both the new schema ({"source": ..., "plugins": [...]}) and
    legacy schema ({"local"/"github"/"name": ..., "plugins": [...]}).
    """
    sources_file = root / "plugin-sources.json"
    if not sources_file.exists():
        return set()
    try:
        data = json.loads(sources_file.read_text(encoding="utf-8"))
        names = set()
        for s in data.get("sources", []):
            plugs = s.get("plugins", [])
            if isinstance(plugs, list):
                names.update(plugs)
        return names
    except Exception as e:
        print(f"  Warning: Failed reading plugin-sources.json: {e}")
        return set()


# plugin_inventory dependencies removed

def sync_source(source_key: str, plugins: list, root: Path, dry_run: bool) -> None:
    """Re-installs all plugins for a given source by calling plugin_add.py."""
    if not plugins:
        return
    plugin_add = root / "plugins" / "plugin-manager" / "scripts" / "plugin_add.py"
    if not plugin_add.exists():
        print(f"  [ERROR] plugin_add.py not found at {plugin_add}")
        return

    plugins_arg = ",".join(plugins)
    cmd = [sys.executable, str(plugin_add), source_key, "--plugins", plugins_arg, "--yes"]
    if dry_run:
        print(f"  [DRY RUN] Would run: {' '.join(cmd)}")
        return
    try:
        subprocess.run(cmd, check=True)
        print(f"  [SYNC] OK: {source_key} -> {plugins}")
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Failed syncing source '{source_key}': {e}")


def _find_missing_artifacts(root: Path, registered_plugins: set) -> list:
    """Return descriptions of missing ownership-tracked artifacts or central copies."""
    missing = []
    for pname in registered_plugins:
        ownership_file = root / ".agents" / "ownership" / f"{pname}.json"
        central_dir = root / ".agents" / "skills" / pname

        if not ownership_file.exists():
            # Fallback checks
            lock_file = root / "skills-lock.json"
            has_skills = False
            if lock_file.exists():
                try:
                    lock = json.loads(lock_file.read_text(encoding="utf-8"))
                    has_skills = any(k.startswith(pname) for k in lock.get("skills", {}).keys())
                except Exception:
                    pass
            if has_skills and not central_dir.exists():
                missing.append(f"{pname} (central copy missing)")
        else:
            try:
                data = json.loads(ownership_file.read_text(encoding="utf-8"))
                for art in data.get("artifacts", []):
                    art_path = root / art
                    if not art_path.exists():
                        missing.append(f"{pname} (artifact missing: {art})")
            except Exception:
                pass
    return missing


def _find_unexpected_skill_dirs(root: Path, registered_plugins: set) -> list:
    """Return descriptions of orphaned directories under .agents/skills/."""
    unexpected = []
    skills_dir = root / ".agents" / "skills"
    valid_skills = set()
    for pname in registered_plugins:
        ownership_file = root / ".agents" / "ownership" / f"{pname}.json"
        if ownership_file.exists():
            try:
                data = json.loads(ownership_file.read_text(encoding="utf-8"))
                for art in data.get("artifacts", []):
                    path_parts = Path(art).parts
                    if len(path_parts) >= 3 and path_parts[0] == ".agents" and path_parts[1] == "skills":
                        valid_skills.add(path_parts[2])
            except Exception:
                pass

        # Fallback local discovery
        plugin_src = root / "plugins" / pname
        if plugin_src.exists() and (plugin_src / "skills").is_dir():
            for item in (plugin_src / "skills").iterdir():
                if item.is_dir():
                    valid_skills.add(item.name)

    if skills_dir.exists():
        for item in skills_dir.iterdir():
            if item.is_dir() and item.name not in valid_skills:
                unexpected.append(f"Orphaned skill directory: {item.relative_to(root)}")
    return unexpected


def validate_agents_state(root: Path, registered_plugins: set) -> None:
    """Scan installed directories and report validation issues."""
    missing = _find_missing_artifacts(root, registered_plugins)
    unexpected = _find_unexpected_skill_dirs(root, registered_plugins)

    if missing or unexpected:
        print("  ⚠️ Validation issues detected:")
        for m in missing:
            print(f"    - Missing: {m}")
        for u in unexpected:
            print(f"    - Unexpected: {u}")
    else:
        print("  ✓ Verification Complete: All registered plugins are clean and accounted for.")


def _read_sources_registry(root: Path) -> tuple:
    """Read plugin-sources.json and return (registered_plugin_names, sources_data).

    Supports both the new schema ({"source": ..., "plugins": [...]}) and
    legacy schema ({"local"/"github"/"name": ..., "plugins": [...]}).
    """
    registered_set = get_installed_plugin_names(root)
    sources_file = root / "plugin-sources.json"
    sources_data = []
    if sources_file.exists():
        try:
            raw = json.loads(sources_file.read_text(encoding="utf-8"))
            for s in raw.get("sources", []):
                src = s.get("source") or s.get("github") or s.get("local") or s.get("name", "")
                plugs = s.get("plugins", [])
                if src and isinstance(plugs, list) and plugs:
                    sources_data.append({"source": src, "plugins": plugs})
        except Exception as e:
            print(f"  Error reading plugin-sources.json: {e}")

    print(f"  {len(registered_set)} registered plugins across {len(sources_data)} sources:")
    for s in sources_data:
        print(f"    [{s['source']}] -> {', '.join(s['plugins'])}")
    return registered_set, sources_data


def _cleanup_stale_sources(sources_data: list, root: Path, dry_run: bool) -> None:
    """Detect locally-sourced plugins whose source directory is gone and clean them up."""
    stale = set()
    for s in sources_data:
        src = s["source"]
        # Only check stale for local paths (not GitHub slugs)
        if src.startswith("/") or src.startswith("./") or src.startswith("plugins/"):
            src_path = Path(src) if src.startswith("/") else root / src
            if not src_path.exists():
                stale.update(s["plugins"])
                print(f"  Stale source (path gone): {src} -> {s['plugins']}")

    if stale:
        print(f"  Cleaning {len(stale)} stale plugin(s)...")
        for plugin in sorted(stale):
            clean_plugin_artifacts(plugin, root, dry_run)
    else:
        print("  No stale local sources detected.")


def _sync_all_registered_sources(sources_data: list, root: Path, dry_run: bool) -> None:
    """Call sync_source for every registered source entry to reinstall its plugins."""
    if not sources_data:
        print("  No sources registered in plugin-sources.json. Nothing to sync.")
        print("  Run plugin_add.py to register and install plugins first.")
        return
    for s in sources_data:
        if s["plugins"]:
            src = s["source"]
            print(f"\n  Source: {src}")
            sync_source(src, s["plugins"], root, dry_run)


def main() -> None:
    """CLI entry point: read registry, clean stale plugins, sync all sources, validate.

    Reads plugin-sources.json to discover all registered plugin sources,
    detects and cleans up stale local-path sources whose directories are gone,
    calls plugin_add.py to reinstall each source (unless --cleanup-only),
    then runs validate_agents_state to confirm .agents/ is consistent.
    """
    parser = argparse.ArgumentParser(description="Sync all plugins from plugin-sources.json registry.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without modifying files.")
    parser.add_argument("--cleanup-only", action="store_true", help="Run cleanup only, skip reinstall.")
    args = parser.parse_args()

    root = Path.cwd()

    print("--- 1. Reading plugin-sources.json Registry ---")
    registered_set, sources_data = _read_sources_registry(root)

    print("\n--- 3. Cleanup Analysis ---")
    _cleanup_stale_sources(sources_data, root, args.dry_run)

    if not args.cleanup_only:
        print(f"\n--- 4. Syncing All Registered Plugins ---")
        _sync_all_registered_sources(sources_data, root, args.dry_run)
    else:
        print("\nSkipping reinstall (--cleanup-only).")

    print("\n--- 5. Post-Sync Validation ---")
    if not args.dry_run:
        validate_agents_state(root, registered_set)
    else:
        print("  [DRY RUN] Skipping validation check.")

    print("\nSync Complete.")


if __name__ == "__main__":
    main()
