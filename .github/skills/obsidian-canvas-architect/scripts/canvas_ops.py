"""
Obsidian Canvas Architect Operations

Purpose: Programmatically create and manipulate Obsidian Canvas (.canvas) files
using JSON Canvas Spec 1.0. Enables agents to generate visual flowcharts,
architecture diagrams, and planning boards with nodes and edges.
"""
import sys
import json
import uuid
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
import os


class CanvasError(Exception):
    """Non-fatal error for canvas operations."""
    pass


# ---------------------------------------------------------------------------
# Schema Validation
# ---------------------------------------------------------------------------
REQUIRED_NODE_FIELDS = {
    "text": ["id", "type", "text", "x", "y", "width", "height"],
    "file": ["id", "type", "file", "x", "y", "width", "height"],
    "link": ["id", "type", "url", "x", "y", "width", "height"],
    "group": ["id", "type", "x", "y", "width", "height"],
}

REQUIRED_EDGE_FIELDS = ["id", "fromNode", "toNode"]
VALID_SIDES = ["top", "right", "bottom", "left"]


def _validate_node(node: Dict[str, Any]) -> Optional[str]:
    """Validate a node against JSON Canvas Spec 1.0. Returns None if valid, error string otherwise."""
    node_type = node.get("type")
    if node_type not in REQUIRED_NODE_FIELDS:
        return f"Unknown node type: {node_type}. Valid: {list(REQUIRED_NODE_FIELDS.keys())}"

    for field in REQUIRED_NODE_FIELDS[node_type]:
        if field not in node:
            return f"Node missing required field '{field}' for type '{node_type}'"

    return None


def _validate_edge(edge: Dict[str, Any], node_ids: set) -> Optional[str]:
    """Validate an edge. Returns None if valid, error string otherwise."""
    for field in REQUIRED_EDGE_FIELDS:
        if field not in edge:
            return f"Edge missing required field '{field}'"

    if edge["fromNode"] not in node_ids:
        return f"Edge references unknown fromNode: {edge['fromNode']}"
    if edge["toNode"] not in node_ids:
        return f"Edge references unknown toNode: {edge['toNode']}"

    for side_field in ["fromSide", "toSide"]:
        if side_field in edge and edge[side_field] not in VALID_SIDES:
            return f"Invalid {side_field}: {edge[side_field]}. Valid: {VALID_SIDES}"

    return None


def _gen_id() -> str:
    """Generate a short unique ID for nodes/edges."""
    return uuid.uuid4().hex[:12]


# ---------------------------------------------------------------------------
# Core Operations
# ---------------------------------------------------------------------------
def read_canvas(filepath: Path) -> Dict[str, Any]:
    """Read and parse a .canvas file."""
    if not filepath.exists():
        return {"error": f"File not found: {filepath}"}

    try:
        content = filepath.read_text(encoding='utf-8')
        data = json.loads(content)

        # Validate structure
        if not isinstance(data, dict):
            return {"error": "Canvas file is not a JSON object", "file": str(filepath)}

        nodes = data.get("nodes", [])
        edges = data.get("edges", [])

        # Validate each node
        warnings = []
        for i, node in enumerate(nodes):
            err = _validate_node(node)
            if err:
                warnings.append(f"Node {i}: {err}")

        # Validate each edge
        node_ids = {n["id"] for n in nodes if "id" in n}
        for i, edge in enumerate(edges):
            err = _validate_edge(edge, node_ids)
            if err:
                warnings.append(f"Edge {i}: {err}")

        return {
            "file": str(filepath),
            "node_count": len(nodes),
            "edge_count": len(edges),
            "nodes": nodes,
            "edges": edges,
            "warnings": warnings if warnings else None
        }

    except json.JSONDecodeError as e:
        return {"error": f"JSON_PARSE_ERROR: {str(e)}", "file": str(filepath)}
    except Exception as e:
        return {"error": f"READ_ERROR: {str(e)}", "file": str(filepath)}


def create_canvas(filepath: Path) -> Dict[str, Any]:
    """Create a new empty .canvas file."""
    if filepath.exists():
        return {"error": f"File already exists: {filepath}"}

    filepath.parent.mkdir(parents=True, exist_ok=True)

    canvas = {"nodes": [], "edges": []}
    content = json.dumps(canvas, indent=2)

    # Atomic write
    tmp_path = filepath.parent / f"{filepath.name}.agent-tmp"
    tmp_path.write_text(content, encoding='utf-8')
    os.rename(str(tmp_path), str(filepath))

    return {"status": "created", "file": str(filepath)}


def add_node(filepath: Path, node_type: str, x: int = 0, y: int = 0,
             width: int = 250, height: int = 60, **kwargs) -> Dict[str, Any]:
    """Add a node to an existing canvas."""
    if not filepath.exists():
        return {"error": f"File not found: {filepath}"}

    try:
        content = filepath.read_text(encoding='utf-8')
        data = json.loads(content)

        node = {
            "id": _gen_id(),
            "type": node_type,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
        }

        # Add type-specific fields
        if node_type == "text":
            node["text"] = kwargs.get("text", "")
        elif node_type == "file":
            node["file"] = kwargs.get("file_path", "")
        elif node_type == "link":
            node["url"] = kwargs.get("url", "")
        elif node_type == "group":
            node["label"] = kwargs.get("label", "")

        # Optional color
        if "color" in kwargs:
            node["color"] = kwargs["color"]

        # Validate before adding
        err = _validate_node(node)
        if err:
            return {"error": f"VALIDATION_ERROR: {err}"}

        if "nodes" not in data:
            data["nodes"] = []
        data["nodes"].append(node)

        # Atomic write
        new_content = json.dumps(data, indent=2)
        tmp_path = filepath.parent / f"{filepath.name}.agent-tmp"
        tmp_path.write_text(new_content, encoding='utf-8')
        os.rename(str(tmp_path), str(filepath))

        return {"status": "node_added", "node_id": node["id"], "file": str(filepath)}

    except json.JSONDecodeError as e:
        return {"error": f"JSON_PARSE_ERROR: {str(e)}"}
    except Exception as e:
        return {"error": f"ADD_NODE_ERROR: {str(e)}"}


def add_edge(filepath: Path, from_node: str, to_node: str,
             from_side: str = "right", to_side: str = "left",
             label: str = None) -> Dict[str, Any]:
    """Add a directional edge between two nodes."""
    if not filepath.exists():
        return {"error": f"File not found: {filepath}"}

    try:
        content = filepath.read_text(encoding='utf-8')
        data = json.loads(content)

        node_ids = {n["id"] for n in data.get("nodes", []) if "id" in n}

        edge = {
            "id": _gen_id(),
            "fromNode": from_node,
            "toNode": to_node,
            "fromSide": from_side,
            "toSide": to_side,
        }
        if label:
            edge["label"] = label

        # Validate
        err = _validate_edge(edge, node_ids)
        if err:
            return {"error": f"VALIDATION_ERROR: {err}"}

        if "edges" not in data:
            data["edges"] = []
        data["edges"].append(edge)

        # Atomic write
        new_content = json.dumps(data, indent=2)
        tmp_path = filepath.parent / f"{filepath.name}.agent-tmp"
        tmp_path.write_text(new_content, encoding='utf-8')
        os.rename(str(tmp_path), str(filepath))

        return {"status": "edge_added", "edge_id": edge["id"], "file": str(filepath)}

    except json.JSONDecodeError as e:
        return {"error": f"JSON_PARSE_ERROR: {str(e)}"}
    except Exception as e:
        return {"error": f"ADD_EDGE_ERROR: {str(e)}"}


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Obsidian Canvas Architect")
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    read_p = subparsers.add_parser('read', help='Read a .canvas file')
    read_p.add_argument('--file', required=True)

    create_p = subparsers.add_parser('create', help='Create a new canvas')
    create_p.add_argument('--file', required=True)

    node_p = subparsers.add_parser('add-node', help='Add a node')
    node_p.add_argument('--file', required=True)
    node_p.add_argument('--type', required=True, choices=['text', 'file', 'link', 'group'])
    node_p.add_argument('--text', help='Text content (for text nodes)')
    node_p.add_argument('--file-path', help='File path (for file nodes)')
    node_p.add_argument('--url', help='URL (for link nodes)')
    node_p.add_argument('--label', help='Label (for group nodes)')
    node_p.add_argument('--x', type=int, default=0)
    node_p.add_argument('--y', type=int, default=0)
    node_p.add_argument('--width', type=int, default=250)
    node_p.add_argument('--height', type=int, default=60)
    node_p.add_argument('--color', help='Node color')

    edge_p = subparsers.add_parser('add-edge', help='Add an edge')
    edge_p.add_argument('--file', required=True)
    edge_p.add_argument('--from-node', required=True)
    edge_p.add_argument('--to-node', required=True)
    edge_p.add_argument('--from-side', default='right', choices=VALID_SIDES)
    edge_p.add_argument('--to-side', default='left', choices=VALID_SIDES)
    edge_p.add_argument('--label', help='Edge label')

    args = parser.parse_args()

    if args.command == 'read':
        print(json.dumps(read_canvas(Path(args.file)), indent=2))
    elif args.command == 'create':
        print(json.dumps(create_canvas(Path(args.file)), indent=2))
    elif args.command == 'add-node':
        kwargs = {}
        if args.text: kwargs["text"] = args.text
        if args.file_path: kwargs["file_path"] = args.file_path
        if args.url: kwargs["url"] = args.url
        if args.label: kwargs["label"] = args.label
        if args.color: kwargs["color"] = args.color
        print(json.dumps(add_node(Path(args.file), args.type, args.x, args.y, args.width, args.height, **kwargs), indent=2))
    elif args.command == 'add-edge':
        print(json.dumps(add_edge(Path(args.file), args.from_node, args.to_node, args.from_side, args.to_side, args.label), indent=2))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
