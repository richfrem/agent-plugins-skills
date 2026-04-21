#!/usr/bin/env python
"""
test_plugin_lifecycle.py
=====================================

Purpose:
    Test harness script to validate the add and remove lifecycle of a plugin.
    Validates the new plugin-sources.json schema (flat "source" key).
    Runs non-interactively using --yes flags.

Layer: Development / Testing

Usage:
    python plugins/plugin-manager/scripts/test_plugin_lifecycle.py
"""

import sys
import json
import subprocess
from pathlib import Path


def run_command(cmd: list) -> None:
    """Executes a command and exits on failure."""
    print(f"\n[RUN] {' '.join(cmd)}")
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"  FAILED (Exit {result.returncode})")
        if result.stdout.strip():
            print("  --- STDOUT ---")
            print(result.stdout)
        if result.stderr.strip():
            print("  --- STDERR ---")
            print(result.stderr)
        sys.exit(result.returncode)
    else:
        print("  SUCCESS")


def verify_sources(label: str, plugin_name: str, expect_present: bool) -> None:
    """Assert plugin-sources.json state matches expectation and uses new schema."""
    sources_file = Path("plugin-sources.json")

    if not sources_file.exists():
        if not expect_present:
            print(f"  PASS {label}: plugin-sources.json absent (cleaned up)")
            return
        print(f"  FAIL {label}: plugin-sources.json does not exist")
        sys.exit(1)

    data = json.loads(sources_file.read_text(encoding="utf-8"))
    sources = data.get("sources", [])

    # Schema validation: every entry must use the new flat "source" key
    for s in sources:
        if "local" in s or "github" in s:
            print(f"  FAIL {label}: Legacy 'local'/'github' key found — migrate to 'source'")
            print(f"       Entry: {s}")
            sys.exit(1)
        if "source" not in s:
            print(f"  FAIL {label}: Entry missing 'source' key: {s}")
            sys.exit(1)

    found = any(plugin_name in s.get("plugins", []) for s in sources)

    if expect_present and found:
        print(f"  PASS {label}: '{plugin_name}' present with correct 'source' schema")
    elif not expect_present and not found:
        print(f"  PASS {label}: '{plugin_name}' correctly absent")
    elif expect_present and not found:
        print(f"  FAIL {label}: '{plugin_name}' NOT found in plugin-sources.json")
        sys.exit(1)
    else:
        print(f"  FAIL {label}: '{plugin_name}' still present after removal")
        sys.exit(1)


def verify_no_duplicates(plugin_name: str) -> None:
    """Assert no plugin appears more than once in any source's plugins array."""
    sources_file = Path("plugin-sources.json")
    if not sources_file.exists():
        return
    data = json.loads(sources_file.read_text(encoding="utf-8"))
    for s in data.get("sources", []):
        plugs = s.get("plugins", [])
        if plugs.count(plugin_name) > 1:
            print(f"  FAIL Duplicate '{plugin_name}' in source: {s.get('source')}")
            sys.exit(1)
    print(f"  PASS No duplicates for '{plugin_name}'")


def main() -> None:
    print("=" * 52)
    print("  Plugin Lifecycle Test Harness")
    print("=" * 52)

    python_exec = sys.executable
    add_script = "plugins/plugin-manager/scripts/plugin_add.py"
    remove_script = "plugins/plugin-manager/scripts/plugin_remove.py"
    sync_script = "plugins/plugin-manager/scripts/sync_with_inventory.py"

    github_source = "richfrem/agent-plugins-skills"
    local_source = "plugins/agent-loops"
    plugin_name = "agent-loops"

    # Phase 1: GitHub install
    print("\n[Phase 1] Install via GitHub source")
    run_command([python_exec, add_script, github_source, "--plugins", plugin_name, "--yes"])
    verify_sources("After GitHub install", plugin_name, expect_present=True)

    # Phase 2: Idempotency check
    print("\n[Phase 2] Re-install (idempotency)")
    run_command([python_exec, add_script, github_source, "--plugins", plugin_name, "--yes"])
    verify_sources("After re-install", plugin_name, expect_present=True)
    verify_no_duplicates(plugin_name)

    # Phase 3: Sync Inventory
    print("\n[Phase 3] Sync via inventory script")
    run_command([python_exec, sync_script])
    verify_sources("After sync", plugin_name, expect_present=True)
    verify_no_duplicates(plugin_name)

    # Phase 4: Remove
    print("\n[Phase 4] Remove via headless flag")
    run_command([python_exec, remove_script, "--plugins", plugin_name, "--yes"])
    verify_sources("After remove", plugin_name, expect_present=False)

    # Phase 5: Local install
    print("\n[Phase 5] Install via local source")
    run_command([python_exec, add_script, local_source, "--yes"])
    verify_sources("After local install", plugin_name, expect_present=True)

    # Phase 6: Sync Inventory locally
    print("\n[Phase 6] Sync local inventory")
    run_command([python_exec, sync_script])
    verify_sources("After local sync", plugin_name, expect_present=True)

    # Phase 7: Remove again
    print("\n[Phase 7] Remove local install")
    run_command([python_exec, remove_script, "--plugins", plugin_name, "--yes"])
    verify_sources("After local remove", plugin_name, expect_present=False)

    print("\n" + "=" * 52)
    print("  All Lifecycle Tests Passed!")
    print("=" * 52 + "\n")


if __name__ == "__main__":
    main()
