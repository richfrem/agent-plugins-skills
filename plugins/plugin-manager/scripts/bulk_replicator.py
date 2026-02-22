#!/usr/bin/env python3
"""
Update All Plugins

Bulk installer that reads a configuration (or installs all) plugins from this repo
into a target project.

Usage:
    update_all_plugins.py --target <project_root> [--link] [--filter <pattern>]

Arguments:
    --target    Target project root directory
    --link      Use symlinks
    --filter    (Optional) Glob pattern to filter plugins (e.g. 'investment-*')
"""

import sys
import argparse
import glob
from pathlib import Path
from plugin_replicator import install_plugin

def main():
    parser = argparse.ArgumentParser(description="Update/Install all plugins into a target project.")
    parser.add_argument("--target", required=True, help="Target project root directory")
    parser.add_argument("--link", action="store_true", help="Use symlinks")
    parser.add_argument("--filter", default="*", help="Glob pattern for plugin names (default: *)")
    
    args = parser.parse_args()
    
    # Locate plugins directory
    current_script = Path(__file__).resolve()
    repo_root = current_script.parents[3]
    plugins_dir = repo_root / 'plugins'
    
    # Find matching plugins
    all_plugins = [p.name for p in plugins_dir.iterdir() if p.is_dir() and not p.name.startswith('.')]
    
    # Apply filter if needed (simple implementation)
    # Using glob on the path
    matched_paths = list(plugins_dir.glob(args.filter))
    matched_names = [p.name for p in matched_paths if p.is_dir() and not p.name.startswith('.')]
    
    print(f"📦 Found {len(matched_names)} plugins matching '{args.filter}'")
    print(f"📂 Target: {args.target}")
    if args.link:
        print("🔗 Mode: Symlink (Dev)")
    else:
        print("cp Mode: Copy (Production)")
        
    print("-" * 40)
    
    success_count = 0
    fail_count = 0
    
    for plugin_name in matched_names:
        print(f"Installing {plugin_name}...")
        if install_plugin(plugin_name, args.target, args.link):
            success_count += 1
        else:
            fail_count += 1
            
    print("-" * 40)
    print(f"🏁 Done. Installed: {success_count}, Failed: {fail_count}")

if __name__ == "__main__":
    main()
