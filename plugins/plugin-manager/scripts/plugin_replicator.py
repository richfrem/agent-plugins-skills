"""
Plugin Replicator

Replicates a plugin from the `central-repo` into a target project.
Designed to support 'monorepo of plugins' workflow where plugins reside in one repo
and are replicated/linked into multiple consumer projects.

Usage:
    plugin_replicator.py --plugin <plugin_name> --target <project_root> [--link]

Arguments:
    --plugin    Name of the plugin directory in 'plugins/' (e.g., 'guardian-onboarding')
    --target    Root directory of the target project (e.g., '../project-sanctuary')
    --link      (Optional) Create a symbolic link instead of copying (Best for dev)
"""

import sys
import shutil
import platform
import argparse
from pathlib import Path

def setup_logger():
    # Simple logger setup
    return print

log = setup_logger()

def install_plugin(plugin_name, target_project_root, use_link=False):
    # 1. Locate Source Plugin
    # This script is in plugins/plugin-manager/scripts/
    # So repo root is ../../../
    current_script = Path(__file__).resolve()
    repo_root = current_script.parents[3]
    plugins_dir = repo_root / 'plugins'
    
    source_plugin_path = plugins_dir / plugin_name
    
    if not source_plugin_path.exists():
        log(f"❌ Error: Source plugin '{plugin_name}' not found at {source_plugin_path}")
        return False
        
    # 2. Locate Target Directory
    # We install into <target_project_root>/.agent/plugins/<plugin_name>
    target_root = Path(target_project_root).resolve()
    if not target_root.exists():
        log(f"❌ Error: Target project directory not found at {target_root}")
        return False
        
    target_plugins_dir = target_root / '.agent' / 'plugins'
    target_plugins_dir.mkdir(parents=True, exist_ok=True)
    
    target_plugin_path = target_plugins_dir / plugin_name
    
    # 3. Clean existing installation
    if target_plugin_path.exists() or target_plugin_path.is_symlink():
        log(f"🧹 Scouring existing installation at {target_plugin_path}...")
        if target_plugin_path.is_symlink():
            target_plugin_path.unlink()
        elif target_plugin_path.is_dir():
            shutil.rmtree(target_plugin_path)
        else:
            target_plugin_path.unlink()

    # 4. Install (Copy or Link)
    try:
        if use_link:
            log(f"🔗 Linking {plugin_name}...")
            # On Windows, requires Admin or Developer Mode for symlinks usually.
            # Using absolute paths for safety.
            target_plugin_path.symlink_to(source_plugin_path, target_is_directory=True)
            log(f"✅ Linked: {target_plugin_path} -> {source_plugin_path}")
        else:
            log(f"cp Copying {plugin_name}...")
            shutil.copytree(source_plugin_path, target_plugin_path)
            log(f"✅ Installed: {target_plugin_path}")
            
        # 5. Post-Install: Check for 'install.py' script in the plugin itself
        # If the plugin has a custom installer, run it? (Optional, maybe for future)
        plugin_install_script = target_plugin_path / 'scripts' / 'install.py'
        if plugin_install_script.exists():
             log(f"ℹ️  Note: This plugin has a custom install script at {plugin_install_script}. You may need to run it.")

        return True

    except Exception as e:
        log(f"❌ Installation failed: {e}")
        # On Windows, symlink errors are common if not admin
        if use_link and platform.system() == "Windows":
            log("👉 Tip: On Windows, you must run this terminal as Administrator to create symlinks, or enable Developer Mode.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Install a plugin into a target project.")
    parser.add_argument("--plugin", required=True, help="Name of the plugin directory")
    parser.add_argument("--target", required=True, help="Target project root directory")
    parser.add_argument("--link", action="store_true", help="Use symlinks (junctions on Windows) instead of copying")
    
    args = parser.parse_args()
    
    print(f"🚀 Bridge Installer: {args.plugin} -> {args.target}")
    success = install_plugin(args.plugin, args.target, args.link)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
