#!/usr/bin/env python3
"""
debug_rlm.py
=====================================

Purpose:
    Debug utility for inspecting RLMConfig state for all known profiles.
    Verifies path resolution, manifest existence, file discovery counts,
    and model configuration without modifying any data.

Layer: Curate / Rlm

Usage:
    python plugins/rlm-factory/skills/rlm-curator/scripts/debug_rlm.py

Related:
    - rlm_config.py (configuration & file collection)
"""
import sys
from pathlib import Path

# ============================================================
# PATHS
# File is at: plugins/rlm-factory/skills/rlm-curator/scripts/debug_rlm.py
# Root is 6 levels up (scripts→rlm-curator→skills→rlm-factory→plugins→ROOT)
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parents[5]
SCRIPT_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from rlm_config import RLMConfig, collect_files
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)


def inspect_profile(profile_name: str) -> None:
    """
    Print a detailed state summary for a single RLM profile.

    Resolves config, checks manifest existence, counts discoverable files,
    and reports the model configuration without writing anything to disk.

    Args:
        profile_name: Name of the profile to inspect.
    """
    print(f"\n{'='*50}")
    print(f"Profile: '{profile_name}'")
    print(f"{'='*50}")
    try:
        config = RLMConfig(profile_name=profile_name)
        print(f"  Description:      {config.description}")
        print(f"  Manifest Path:    {config.manifest_path}")
        print(f"  Manifest Exists:  {config.manifest_path.exists()}")
        print(f"  Cache Path:       {config.cache_path}")
        print(f"  Include Patterns: {config.include_patterns}")
        print(f"  Allowed Suffixes: {config.allowed_suffixes}")
        print(f"  LLM Model:        {config.llm_model}")
        files = collect_files(config)
        print(f"  Files Found:      {len(files)}")
        if files:
            print(f"  Sample File:      {files[0].relative_to(PROJECT_ROOT)}")
    except Exception as e:
        print(f"  ❌ Error: {e}")


if __name__ == "__main__":
    # Inspect all standard profiles
    for profile in ["plugins", "tools"]:
        inspect_profile(profile)
