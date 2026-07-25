#!/usr/bin/env python3
"""
Unit tests for Friction Hotspot Clustering Engine (friction_cluster_agent.py)
========================================================================
Purpose:
    Tests label aggregation (`area:*`, `plugin:*`, `type:*`) and recommendation logic
    for friction hotspot clustering.

Key Input Dependencies:
    - friction_cluster_agent.py
"""

from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from friction_cluster_agent import cluster_friction_issues


def test_cluster_friction_issues():
    """Test clustering of friction issues by area/plugin and type labels."""
    issues = [
        {"number": 1, "title": "Script x.py failed on missing dependency", "labels": [{"name": "area:scripts"}, {"name": "type:friction"}]},
        {"number": 2, "title": "Script y.py failed on missing dependency", "labels": [{"name": "area:scripts"}, {"name": "type:friction"}]},
        {"number": 3, "title": "Doc link broken in README", "labels": [{"name": "area:docs"}, {"name": "type:documentation"}]}
    ]
    report = cluster_friction_issues(issues)
    assert report["total_issues"] == 3
    assert "area:scripts" in report["top_areas"]
    assert report["top_areas"]["area:scripts"] == 2
    assert "type:friction" in report["top_types"]
    assert report["top_types"]["type:friction"] == 2
    assert len(report["recommendations"]) == 1
    assert "area:scripts" in report["recommendations"][0]
