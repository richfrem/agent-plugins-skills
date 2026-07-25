#!/usr/bin/env python3
"""
Friction Hotspot Clustering Engine
=====================================
Purpose:
    Parses open and closed GitHub friction issues to aggregate hotspots, recurring failure classes, and map debt.

Layer: Retrieve / Curate
Key Input Dependencies:
    - GitHub issues list (JSON format with labels)
"""

from typing import List, Dict, Any
from collections import Counter


def cluster_friction_issues(issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Clusters GitHub issues by area/plugin and type labels to identify friction hotspots.

    Args:
        issues: A list of issue dictionaries containing label objects/strings.

    Returns:
        A dictionary report summarizing total issues, top areas/plugins, top types, and recommendations.
    """
    area_counts: Counter = Counter()
    type_counts: Counter = Counter()

    for issue in issues:
        raw_labels = issue.get("labels", [])
        labels = []
        for l in raw_labels:
            if isinstance(l, dict) and "name" in l:
                labels.append(l["name"])
            elif isinstance(l, str):
                labels.append(l)

        for label in labels:
            if label.startswith("area:") or label.startswith("plugin:"):
                area_counts[label] += 1
            elif label.startswith("type:"):
                type_counts[label] += 1

    return {
        "total_issues": len(issues),
        "top_areas": dict(area_counts.most_common(5)),
        "top_types": dict(type_counts.most_common(5)),
        "recommendations": [
            f"Review {area} ({count} friction events)" for area, count in area_counts.items() if count >= 2
        ]
    }
