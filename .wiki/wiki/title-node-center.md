---
concept: title-node-center
source: plugin-code
source_file: obsidian-wiki-engine/scripts/canvas_gen.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.009942+00:00
cluster: wiki
content_hash: 378d149a13853761
---

# Title node (center)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
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


*(content truncated)*

## See Also

- [[task-number-title]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/scripts/canvas_gen.py`
- **Indexed:** 2026-04-27T05:21:04.009942+00:00
