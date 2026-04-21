#!/usr/bin/env python
"""
test_plugin_lifecycle.py
=====================================

Purpose:
    Test harness script to validate the add and remove lifecycle of a plugin.
    Runs non-interactively using `--yes` flags.

Layer: Development / Testing

Usage:
    python plugins/plugin-manager/scripts/test_plugin_lifecycle.py
"""

import sys
import subprocess
from pathlib import Path


def run_command(cmd: list[str]) -> None:
    """
    Executes a shell command via subprocess and checks for errors.

    Args:
        cmd: List of string arguments representing the command.

    Raises:
        subprocess.CalledProcessError: If the command returns a non-zero exit code.
    """
    print(f"\n[TESTING] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"FAILED (Exit {result.returncode})")
        print("--- STDOUT ---")
        print(result.stdout)
        print("--- STDERR ---")
        print(result.stderr)
        sys.exit(result.returncode)
    else:
        print("SUCCESS")
        print("--- STDOUT ---")
        print(result.stdout)


def main() -> None:
    """
    Main execution block for the test harness.
    Runs plugin_add.py and plugin_remove.py in sequence.
    """
    print("====================================")
    print(" Plugin Lifecycle Test Harness ")
    print("====================================")
    
    python_exec = sys.executable
    add_script = "plugins/plugin-manager/scripts/plugin_add.py"
    remove_script = "plugins/plugin-manager/scripts/plugin_remove.py"
    
    plugin_repo = "richfrem/agent-plugins-skills"
    plugin_name = "agent-loops"
    
    # 1. Install agent-loops remotely
    cmd_add = [
        python_exec,
        add_script,
        plugin_repo,
        "--plugins", plugin_name,
        "--yes"
    ]
    run_command(cmd_add)
    
    # 2. Verify JSON updated
    print("\n[TESTING] Verifying plugin-sources.json state...")
    sources_file = Path("plugin-sources.json")
    if sources_file.exists():
        import json
        data = json.loads(sources_file.read_text(encoding="utf-8"))
        found = any(plugin_name in s.get("plugins", []) for s in data.get("sources", []))
        if found:
            print("SUCCESS: Found plugin name in plugin-sources.json arrays")
        else:
            print("FAILED: plugin name NOT found in plugin-sources.json arrays")
            sys.exit(1)
    else:
        print("FAILED: plugin-sources.json does not exist")
        sys.exit(1)
            
    # 3. Remove agent-loops
    cmd_remove = [
        python_exec,
        remove_script,
        "--plugins", plugin_name,
        "--yes"
    ]
    run_command(cmd_remove)
    
    # 4. Verify JSON removed
    print("\n[TESTING] Verifying plugin-sources.json state after removal...")
    if sources_file.exists():
        import json
        data = json.loads(sources_file.read_text(encoding="utf-8"))
        found = any(plugin_name in s.get("plugins", []) for s in data.get("sources", []))
        if not found:
            print("SUCCESS: Plugin properly scrubbed from plugin-sources.json")
        else:
            print("FAILED: Plugin STILL in plugin-sources.json arrays after removal")
            sys.exit(1)
    else:
        print("SUCCESS: plugin-sources.json does not exist (cleaned up completely)")
            
    print("\n====================================")
    print(" All Lifecycle Tests Passed! ")
    print("====================================")

if __name__ == "__main__":
    main()
