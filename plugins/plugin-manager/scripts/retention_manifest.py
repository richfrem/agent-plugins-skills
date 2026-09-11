#!/usr/bin/env python3
"""
retention_manifest.py
=====================

Purpose:
    Data model helpers to load, save, merge, and inspect component retention
    states for the Component Retention Pruner system (plugin-retention.json).

Layer: Plugin Manager / Data Access

Interfaces:
    - load_manifest(path: Path) -> dict
    - save_manifest(path: Path, data: dict) -> None
    - merge_installed_components(manifest: dict, plugin_name: str, artifacts: list[str]) -> dict
    - get_component_states(manifest: dict) -> tuple[dict[str, bool], dict[str, bool], dict[str, bool]]
"""

import json
import sys
import types
from pathlib import Path
from typing import Optional, Tuple, Dict, List, Any


def parse_artifact(artifact: str) -> Tuple[Optional[str], Optional[str]]:
    """Identifies the component type ('skills', 'rules', 'agents') and its name from an artifact path.

    Args:
        artifact: Path string or representation of an installed artifact.

    Returns:
        (component_type, component_name) or (None, None) if not recognized.
    """
    normalized = str(artifact).replace("\\", "/").strip()
    parts = [p for p in normalized.split("/") if p and p != "."]

    # 1. Skills: look for path segment following 'skills'
    if "skills" in parts:
        idx = parts.index("skills")
        if idx + 1 < len(parts):
            return "skills", parts[idx + 1]

    # 2. Rules: look for rule files under '.agent/rules', '.agents/rules', or 'rules'
    if "rules" in parts:
        idx = parts.index("rules")
        if idx + 1 < len(parts):
            return "rules", parts[-1]

    # 3. Agents: look for agent files under '.agents/agents' or 'agents'
    # Note: avoid matching the root '.agents' directory as 'agents'
    agent_indices = [i for i, p in enumerate(parts) if p == "agents"]
    if agent_indices:
        idx = agent_indices[-1]
        if idx + 1 < len(parts):
            return "agents", parts[-1]

    return None, None


def load_manifest(path: Path) -> Dict[str, Any]:
    """Loads and parses the retention manifest from a file path.

    Args:
        path: Path to the JSON manifest file.

    Returns:
        Parsed manifest dictionary.
    """
    p = Path(path)
    content = p.read_text(encoding="utf-8")
    return json.loads(content)


def save_manifest(path: Path, data: Dict[str, Any]) -> None:
    """Saves the retention manifest data to a file path as formatted JSON.

    Args:
        path: Path to the target JSON manifest file.
        data: Manifest dictionary to save.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, indent=2) + "\n"
    p.write_text(content, encoding="utf-8")


def merge_installed_components(
    manifest: Dict[str, Any],
    plugin_name: str,
    artifacts: List[str],
    overwrite_existing: bool = False,
) -> Dict[str, Any]:
    """Merges deployed artifact paths for a plugin into the retention manifest data model.

    Newly discovered skills, rules, and agents are recorded as retained (True).
    Components already present in the manifest retain their current boolean state
    unless overwrite_existing is True.

    Args:
        manifest: The dictionary containing retention manifest data.
        plugin_name: The name of the plugin whose artifacts are being merged.
        artifacts: List of artifact path strings deployed for the plugin.
        overwrite_existing: If True, existing components in the manifest are set to True.
            Defaults to False to preserve user retention choices.

    Returns:
        The updated manifest dictionary.
    """
    if "plugins" not in manifest or not isinstance(manifest["plugins"], dict):
        manifest["plugins"] = {}

    if plugin_name not in manifest["plugins"] or not isinstance(manifest["plugins"][plugin_name], dict):
        manifest["plugins"][plugin_name] = {
            "skills": {},
            "rules": {},
            "agents": {},
        }

    plugin_entry = manifest["plugins"][plugin_name]
    for key in ("skills", "rules", "agents"):
        if key not in plugin_entry or not isinstance(plugin_entry[key], dict):
            plugin_entry[key] = {}

    for artifact in artifacts:
        ctype, cname = parse_artifact(str(artifact))
        if ctype and cname:
            if overwrite_existing or cname not in plugin_entry[ctype]:
                plugin_entry[ctype][cname] = True

    return manifest


def get_component_states(
    manifest: Dict[str, Any],
) -> Tuple[Dict[str, bool], Dict[str, bool], Dict[str, bool]]:
    """Extracts aggregated boolean retention states for skills, rules, and agents across all plugins in the manifest.

    Args:
        manifest: The dictionary containing retention manifest data.

    Returns:
        A 3-tuple of (skills, rules, agents), each being a dict[str, bool] mapping component name to retention state.
    """
    skills: Dict[str, bool] = {}
    rules: Dict[str, bool] = {}
    agents: Dict[str, bool] = {}

    plugins = manifest.get("plugins", {})
    if isinstance(plugins, dict):
        for plugin_data in plugins.values():
            if not isinstance(plugin_data, dict):
                continue
            for s_name, s_state in plugin_data.get("skills", {}).items():
                skills[str(s_name)] = bool(s_state)
            for r_name, r_state in plugin_data.get("rules", {}).items():
                rules[str(r_name)] = bool(r_state)
            for a_name, a_state in plugin_data.get("agents", {}).items():
                agents[str(a_name)] = bool(a_state)

    return skills, rules, agents


# Register compatibility alias under plugins.plugin_manager.scripts.retention_manifest
if "plugins.plugin_manager" not in sys.modules:
    sys.modules["plugins.plugin_manager"] = types.ModuleType("plugins.plugin_manager")
if "plugins.plugin_manager.scripts" not in sys.modules:
    sys.modules["plugins.plugin_manager.scripts"] = types.ModuleType("plugins.plugin_manager.scripts")
sys.modules["plugins.plugin_manager.scripts.retention_manifest"] = sys.modules[__name__]
