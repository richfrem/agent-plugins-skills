#!/usr/bin/env python3
"""
debug_rlm.py (CLI)
=====================================

Purpose:
    Debug utility to inspect RLMConfig state for a given profile.
    Verifies path resolution, manifest loading, and file discovery.
"""

import sys
from pathlib import Path

# Paths standardization
PROJECT_ROOT = Path(__file__).resolve().parents[5]
SCRIPT_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from rlm_config import RLMConfig, collect_files

    for profile_name in ["plugins", "tools"]:
        print(f"\n{'='*50}")
        print(f"--- Profile: '{profile_name}' ---")
        try:
            config = RLMConfig(profile_name=profile_name)
            print(f"  Manifest Path: {config.manifest_path}")
            print(f"  Manifest Exists: {config.manifest_path.exists()}")
            print(f"  Cache Path: {config.cache_path}")
            print(f"  Include Patterns: {config.include_patterns}")
            print(f"  Allowed Suffixes: {config.allowed_suffixes}")
            print(f"  LLM Model: {config.llm_model}")
            files = collect_files(config)
            print(f"  Files Found: {len(files)}")
            if files:
                print(f"  Sample: {files[0].relative_to(PROJECT_ROOT)}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

except ImportError as e:
    print(f"❌ Import Error: {e}")
