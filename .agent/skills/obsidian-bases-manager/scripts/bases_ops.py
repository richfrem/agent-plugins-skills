"""
Obsidian Bases Manager Operations

Purpose: Read and manipulate Obsidian Bases (.base) files.
These YAML-based files define database-like views (tables, cards, grids)
over vault notes. This module handles row appending, cell updates,
and view config preservation using ruamel.yaml for lossless round-tripping.
"""
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from ruamel.yaml import YAML
    _yaml = YAML()
    _yaml.preserve_quotes = True
    _yaml.default_flow_style = False
    HAS_RUAMEL = True
except ImportError:
    HAS_RUAMEL = False
    print("WARNING: ruamel.yaml required. Install: pip install ruamel.yaml", file=sys.stderr)


class BasesError(Exception):
    """Non-fatal error for bases operations. Reports cleanly instead of crashing."""
    pass


def read_base(filepath: Path) -> Dict[str, Any]:
    """Read and parse a .base file. Returns the parsed YAML structure."""
    if not HAS_RUAMEL:
        return {"error": "ruamel.yaml not installed"}

    if not filepath.exists():
        return {"error": f"File not found: {filepath}"}

    if not str(filepath).endswith('.base'):
        return {"error": f"Not a .base file: {filepath}"}

    try:
        from io import StringIO
        content = filepath.read_text(encoding='utf-8')
        data = _yaml.load(StringIO(content))

        if data is None:
            return {"error": "Empty or invalid .base file", "file": str(filepath)}

        result = {
            "file": str(filepath),
            "data": dict(data) if data else {},
        }

        # Extract row count if data has a recognizable structure
        if isinstance(data, dict):
            for key in ['rows', 'data', 'entries', 'items']:
                if key in data and isinstance(data[key], list):
                    result["row_count"] = len(data[key])
                    break

        return result

    except Exception as e:
        return {"error": f"YAML_PARSE_ERROR: {str(e)}", "file": str(filepath)}


def append_row(filepath: Path, row_data: Dict[str, Any]) -> Dict[str, Any]:
    """Append a new row to a .base file's data array."""
    if not HAS_RUAMEL:
        return {"error": "ruamel.yaml not installed"}

    if not filepath.exists():
        return {"error": f"File not found: {filepath}"}

    try:
        from io import StringIO
        content = filepath.read_text(encoding='utf-8')
        data = _yaml.load(StringIO(content))

        if data is None:
            return {"error": "Empty or invalid .base file"}

        # Find the data array (try common keys)
        data_key = None
        for key in ['rows', 'data', 'entries', 'items']:
            if key in data and isinstance(data[key], list):
                data_key = key
                break

        if data_key is None:
            # Create a 'rows' array if none exists
            data['rows'] = []
            data_key = 'rows'

        data[data_key].append(row_data)

        # Write back atomically
        stream = StringIO()
        _yaml.dump(data, stream)
        new_content = stream.getvalue()

        # Use atomic write from vault_ops
        tmp_path = filepath.parent / f"{filepath.name}.agent-tmp"
        import os
        tmp_path.write_text(new_content, encoding='utf-8')
        os.rename(str(tmp_path), str(filepath))

        return {"status": "row_appended", "file": str(filepath), "row_count": len(data[data_key])}

    except Exception as e:
        return {"error": f"APPEND_ERROR: {str(e)}", "file": str(filepath)}


def update_cell(filepath: Path, row_index: int, column: str, value: Any) -> Dict[str, Any]:
    """Update a specific cell in a .base file."""
    if not HAS_RUAMEL:
        return {"error": "ruamel.yaml not installed"}

    if not filepath.exists():
        return {"error": f"File not found: {filepath}"}

    try:
        from io import StringIO
        content = filepath.read_text(encoding='utf-8')
        data = _yaml.load(StringIO(content))

        if data is None:
            return {"error": "Empty or invalid .base file"}

        # Find the data array
        data_key = None
        for key in ['rows', 'data', 'entries', 'items']:
            if key in data and isinstance(data[key], list):
                data_key = key
                break

        if data_key is None:
            return {"error": "No data array found in .base file"}

        rows = data[data_key]
        if row_index < 0 or row_index >= len(rows):
            return {"error": f"Row index {row_index} out of range (0-{len(rows)-1})"}

        if not isinstance(rows[row_index], dict):
            return {"error": f"Row {row_index} is not a dict, cannot update cell"}

        old_value = rows[row_index].get(column, "<not set>")
        rows[row_index][column] = value

        # Write back atomically
        stream = StringIO()
        _yaml.dump(data, stream)
        new_content = stream.getvalue()

        tmp_path = filepath.parent / f"{filepath.name}.agent-tmp"
        import os
        tmp_path.write_text(new_content, encoding='utf-8')
        os.rename(str(tmp_path), str(filepath))

        return {
            "status": "cell_updated",
            "file": str(filepath),
            "row": row_index,
            "column": column,
            "old_value": str(old_value),
            "new_value": str(value)
        }

    except Exception as e:
        return {"error": f"UPDATE_ERROR: {str(e)}", "file": str(filepath)}


def main():
    parser = argparse.ArgumentParser(description="Obsidian Bases Manager")
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    read_p = subparsers.add_parser('read', help='Read a .base file')
    read_p.add_argument('--file', required=True)

    append_p = subparsers.add_parser('append-row', help='Append a row')
    append_p.add_argument('--file', required=True)
    append_p.add_argument('--data', nargs='+', required=True, help='key=value pairs')

    update_p = subparsers.add_parser('update-cell', help='Update a cell')
    update_p.add_argument('--file', required=True)
    update_p.add_argument('--row-index', type=int, required=True)
    update_p.add_argument('--column', required=True)
    update_p.add_argument('--value', required=True)

    args = parser.parse_args()

    if args.command == 'read':
        print(json.dumps(read_base(Path(args.file)), indent=2, default=str))
    elif args.command == 'append-row':
        row = {}
        for kv in args.data:
            k, v = kv.split('=', 1)
            row[k] = v
        print(json.dumps(append_row(Path(args.file), row), indent=2))
    elif args.command == 'update-cell':
        print(json.dumps(update_cell(Path(args.file), args.row_index, args.column, args.value), indent=2))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
