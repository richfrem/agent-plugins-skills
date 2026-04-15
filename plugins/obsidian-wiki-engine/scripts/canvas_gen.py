#!/usr/bin/env python3
"""
canvas_gen.py
=====================================

Purpose:
    Auto-generate Obsidian Canvas (.canvas) files from wiki concept clusters.
    Creates one canvas per cluster showing concepts as nodes with edges
    representing wikilink relationships.

Layer: Visualize / Wiki

Usage:
    python ./scripts/canvas_gen.py --wiki-root /path/to/wiki-root
    python ./scripts/canvas_gen.py --wiki-root /path/to/wiki-root --cluster arch-docs
    python ./scripts/canvas_gen.py --wiki-root /path/to/wiki-root --output /path/to/output.canvas

Related:
    - wiki_builder.py  (generates the wiki nodes this script reads)
    - raw_manifest.py  (wiki root resolution)
    - obsidian-canvas-architect skill (manual canvas editing)
"""
import sys
import json
import argparse
import re
import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from raw_manifest import WikiSourceConfig

NODE_WIDTH = 250
NODE_HEIGHT = 80
CLUSTER_RADIUS_BASE = 400
WIKILINK_PATTERN = re.compile(r"\[\[([^\]|#]+)")


def _extract_wikilinks(node_content: str) -> Set[str]:
    """
    Extract all [[wikilink]] targets from a wiki node file.

    Args:
        node_content: Raw markdown content of the wiki node.

    Returns:
        Set of linked concept slugs.
    """
    return {m.group(1).strip() for m in WIKILINK_PATTERN.finditer(node_content)}


def _layout_circle(concepts: List[str], center_x: int = 0, center_y: int = 0) -> Dict[str, tuple]:
    """
    Arrange concept nodes in a circle for a cluster canvas.

    Args:
        concepts:  List of concept slugs.
        center_x:  Canvas center X coordinate.
        center_y:  Canvas center Y coordinate.

    Returns:
        Dict mapping concept -> (x, y) position.
    """
    n = len(concepts)
    if n == 0:
        return {}
    radius = max(CLUSTER_RADIUS_BASE, n * 60)
    positions: Dict[str, tuple] = {}
    for i, concept in enumerate(concepts):
        angle = (2 * math.pi * i) / n
        x = int(center_x + radius * math.cos(angle))
        y = int(center_y + radius * math.sin(angle))
        positions[concept] = (x, y)
    return positions


def build_cluster_canvas(
    cluster_name: str,
    concepts: List[str],
    wiki_root: Path,
) -> Dict[str, Any]:
    """
    Build a JSON Canvas spec for one cluster of wiki concepts.

    Nodes represent concept wiki files. Edges represent wikilink relationships
    found in the wiki node content.

    Args:
        cluster_name: Name of the cluster (used as canvas title node).
        concepts:     List of concept slugs in this cluster.
        wiki_root:    Root of the wiki output directory.

    Returns:
        JSON Canvas spec dict (JSON Canvas Spec 1.0).
    """
    positions = _layout_circle(concepts)
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    concept_set = set(concepts)

    # Title node (center)
    nodes.append({
        "id": f"_title_{cluster_name}",
        "type": "text",
        "text": f"# {cluster_name.replace('-', ' ').title()}",
        "x": -NODE_WIDTH // 2,
        "y": -NODE_HEIGHT // 2,
        "width": NODE_WIDTH,
        "height": NODE_HEIGHT,
        "color": "1",
    })

    edge_set: Set[tuple] = set()

    for concept, (x, y) in positions.items():
        node_id = f"node_{concept}"
        node_file = wiki_root / "wiki" / f"{concept}.md"
        # Use file reference node if the wiki node exists
        if node_file.exists():
            nodes.append({
                "id": node_id,
                "type": "file",
                "file": str(node_file.relative_to(wiki_root)).replace("\\", "/"),
                "x": x,
                "y": y,
                "width": NODE_WIDTH,
                "height": NODE_HEIGHT,
            })
        else:
            nodes.append({
                "id": node_id,
                "type": "text",
                "text": concept,
                "x": x,
                "y": y,
                "width": NODE_WIDTH,
                "height": NODE_HEIGHT,
            })

        # Extract wikilinks and create edges
        if node_file.exists():
            try:
                content = node_file.read_text(encoding="utf-8")
                for link_target in _extract_wikilinks(content):
                    if link_target in concept_set and link_target != concept:
                        edge_key = tuple(sorted([concept, link_target]))
                        if edge_key not in edge_set:
                            edge_set.add(edge_key)
                            edges.append({
                                "id": f"edge_{concept}_{link_target}",
                                "fromNode": node_id,
                                "fromSide": "right",
                                "toNode": f"node_{link_target}",
                                "toSide": "left",
                            })
            except Exception:
                pass

    return {"nodes": nodes, "edges": edges}


def main() -> None:
    """Parse CLI arguments and generate canvas files for wiki clusters."""
    parser = argparse.ArgumentParser(
        description="Generate Obsidian Canvas files from wiki concept clusters"
    )
    parser.add_argument("--wiki-root", required=True, help="Path to the wiki root directory")
    parser.add_argument("--cluster", default=None, help="Generate canvas for one cluster only")
    parser.add_argument("--output", default=None,
                        help="Output path for canvas file (default: {wiki-root}/wiki/_{cluster}.canvas)")
    args = parser.parse_args()

    wiki_root = Path(args.wiki_root).resolve()
    wiki_dir = wiki_root / "wiki"

    if not wiki_dir.exists():
        print(f"[ERROR] Wiki directory not found: {wiki_dir}")
        print("        Run /wiki-ingest first.")
        sys.exit(1)

    # Group concepts by cluster (from frontmatter)
    clusters: Dict[str, List[str]] = {}
    cluster_pattern = re.compile(r"^cluster:\s*(.+)$", re.MULTILINE)

    for node_file in sorted(wiki_dir.glob("*.md")):
        if node_file.name.startswith("_"):
            continue
        try:
            content = node_file.read_text(encoding="utf-8")
        except Exception:
            continue
        match = cluster_pattern.search(content)
        cluster_name = match.group(1).strip() if match else "unclustered"
        clusters.setdefault(cluster_name, []).append(node_file.stem)

    if not clusters:
        print("[WARN] No wiki nodes found. Run /wiki-ingest first.")
        return

    target_clusters = [args.cluster] if args.cluster else list(clusters.keys())

    for cluster_name in target_clusters:
        if cluster_name not in clusters:
            print(f"[WARN] Cluster '{cluster_name}' not found.")
            continue

        concepts = clusters[cluster_name]
        canvas_spec = build_cluster_canvas(cluster_name, concepts, wiki_root)

        if args.output and args.cluster:
            out_path = Path(args.output)
        else:
            out_path = wiki_dir / f"_{cluster_name}.canvas"

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(canvas_spec, indent=2), encoding="utf-8")
        print(f"[OK] Canvas written: {out_path} ({len(concepts)} nodes, {len(canvas_spec['edges'])} edges)")


if __name__ == "__main__":
    main()
