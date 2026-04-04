#!/usr/bin/env python3
"""
build_capability_index.py
=========================
Scans all plugin.json files in the plugins/ directory and builds a
capability → [plugin_name, ...] index from the "capabilities" array field.

Outputs:
  - capability-index.json   Written to plugins/tool-inventory/assets/capability-index.json
  - stdout                  Human-readable report

Usage:
    python3 plugins/tool-inventory/scripts/build_capability_index.py
    python3 plugins/tool-inventory/scripts/build_capability_index.py --plugins-dir /path/to/plugins

Exit codes:
    0 — success
    1 — no plugin.json files found
"""

import argparse
import json
import pathlib
import sys
from collections import defaultdict
from datetime import datetime, timezone


def find_plugin_jsons(plugins_dir: pathlib.Path) -> list[pathlib.Path]:
    """Return all .claude-plugin/plugin.json files at plugin root level."""
    return sorted(plugins_dir.glob("*/.claude-plugin/plugin.json"))


def build_index(plugin_files: list[pathlib.Path]) -> tuple[dict, list[dict], list[str]]:
    """
    Parse each plugin.json and invert the capabilities array.

    Returns:
        capability_index: {capability: [plugin_name, ...]}
        plugin_manifests: [{name, capabilities, version}]
        warnings: list of warning strings
    """
    capability_index: dict[str, list[str]] = defaultdict(list)
    plugin_manifests: list[dict] = []
    warnings: list[str] = []

    for pjson_path in plugin_files:
        try:
            data = json.loads(pjson_path.read_text())
        except json.JSONDecodeError as exc:
            warnings.append(f"JSON parse error in {pjson_path}: {exc}")
            continue

        plugin_name = data.get("name", pjson_path.parent.parent.name)
        capabilities = data.get("capabilities", [])

        if not capabilities:
            warnings.append(f"No 'capabilities' field in {plugin_name} ({pjson_path})")
        else:
            for cap in capabilities:
                capability_index[cap].append(plugin_name)

        plugin_manifests.append({
            "name": plugin_name,
            "version": data.get("version", "unknown"),
            "capabilities": capabilities,
            "path": str(pjson_path),
        })

    return dict(sorted(capability_index.items())), plugin_manifests, warnings


def write_index(index: dict, manifests: list[dict], output_path: pathlib.Path) -> None:
    """Write the capability index and full plugin manifest to a JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schema_version": "1.0",
        "total_plugins": len(manifests),
        "total_capabilities": len(index),
        "capability_index": index,
        "plugin_manifests": manifests,
    }
    output_path.write_text(json.dumps(payload, indent=2) + "\n")


def print_report(index: dict, manifests: list[dict], warnings: list[str]) -> None:
    """Print a human-readable capability index report."""
    print("=" * 60)
    print("CAPABILITY INDEX REPORT")
    print(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Plugins scanned: {len(manifests)}")
    print(f"Unique capabilities: {len(index)}")
    print("=" * 60)

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"   {w}")

    print("\n📋 CAPABILITY → PROVIDER MAPPING\n")
    for cap, providers in sorted(index.items()):
        provider_str = ", ".join(providers)
        print(f"  ~~{cap:<35} → {provider_str}")

    print("\n📦 PLUGIN MANIFEST\n")
    for m in sorted(manifests, key=lambda x: x["name"]):
        caps = ", ".join(m["capabilities"]) if m["capabilities"] else "(none)"
        print(f"  {m['name']:<40} v{m['version']:<8} [{caps}]")

    print("\n" + "=" * 60)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plugins-dir",
        default="plugins",
        help="Path to the plugins/ directory (default: plugins/)",
    )
    parser.add_argument(
        "--output",
        default="plugins/tool-inventory/assets/capability-index.json",
        help="Output path for the JSON index file",
    )
    args = parser.parse_args()

    plugins_dir = pathlib.Path(args.plugins_dir)
    if not plugins_dir.is_dir():
        print(f"ERROR: plugins directory not found: {plugins_dir}", file=sys.stderr)
        return 1

    plugin_files = find_plugin_jsons(plugins_dir)
    if not plugin_files:
        print(f"ERROR: no plugin.json files found under {plugins_dir}", file=sys.stderr)
        return 1

    capability_index, manifests, warnings = build_index(plugin_files)
    output_path = pathlib.Path(args.output)
    write_index(capability_index, manifests, output_path)
    print_report(capability_index, manifests, warnings)
    print(f"\n✅ Index written to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
