#!/usr/bin/env python3
"""
plugins/tool-inventory/skills/tool-inventory/scripts/generate_tools_manifest.py
====================================
Purpose:
    Scans the plugins/ directory and generates a flat JSON manifest
    of all executable scripts (.py, .js, .sh) organized by plugin name.

Layer: Curate / Discovery

Usage:
    python3 plugins/tool-inventory/skills/tool-inventory/scripts/generate_tools_manifest.py
    python3 plugins/tool-inventory/skills/tool-inventory/scripts/generate_tools_manifest.py --output plugins/tools_manifest.json

Output:
    - plugins/tools_manifest.json (default)
"""
import json
import argparse
import ast
from pathlib import Path
from datetime import datetime

# Script lives at: plugins/<plugin>/skills/<skill>/scripts/
# parents[4] = plugins/   parents[5] = project root
PLUGINS_DIR = Path(__file__).resolve().parents[4]  # → .../plugins/
ROOT = PLUGINS_DIR.parent                           # → project root

SCRIPT_EXTENSIONS = {".py", ".js", ".sh"}

SKIP_NAMES = {"__init__.py"}
SKIP_DIRS = {"node_modules", ".venv", "venv", "__pycache__", ".git"}


def extract_purpose(file_path: Path) -> str:
    """Extract the first 'Purpose:' docstring line from a Python file."""
    if file_path.suffix != ".py":
        return ""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                docstring = ast.get_docstring(node)
                if docstring:
                    for line in docstring.splitlines():
                        stripped = line.strip()
                        if stripped.startswith("Purpose:"):
                            return stripped[len("Purpose:"):].strip()
                    # Return first non-empty line of docstring if no Purpose: found
                    for line in docstring.splitlines():
                        if line.strip():
                            return line.strip()
                break
    except Exception:
        pass
    return ""


def main():
    parser = argparse.ArgumentParser(description="Generate a tool manifest from plugins/")
    parser.add_argument("--output", default="plugins/tools_manifest.json", help="Output path")
    args = parser.parse_args()

    manifest = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "source": "plugins/",
            "description": "Auto-discovered scripts from the plugins/ hierarchy"
        },
        "plugins": {}
    }

    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_dir.is_dir() or plugin_dir.name.startswith("."):
            continue

        plugin_name = plugin_dir.name
        scripts = []

        for file_path in sorted(plugin_dir.rglob("*")):
            # Skip exclusions
            if any(p in SKIP_DIRS for p in file_path.parts):
                continue
            if file_path.name in SKIP_NAMES:
                continue
            if file_path.suffix not in SCRIPT_EXTENSIONS:
                continue
            if not file_path.is_file():
                continue

            rel_path = str(file_path.relative_to(ROOT))
            entry = {
                "name": file_path.name,
                "path": rel_path,
                "purpose": extract_purpose(file_path),
                "type": {"py": "python", "js": "javascript", "sh": "bash"}.get(file_path.suffix.lstrip("."), "unknown")
            }
            scripts.append(entry)

        if scripts:
            manifest["plugins"][plugin_name] = {
                "count": len(scripts),
                "scripts": scripts
            }

    output_path = ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2))

    total = sum(p["count"] for p in manifest["plugins"].values())
    print(f"✅ Manifest written to {output_path.relative_to(ROOT)}")
    print(f"   Plugins: {len(manifest['plugins'])} | Total Scripts: {total}")


if __name__ == "__main__":
    main()
