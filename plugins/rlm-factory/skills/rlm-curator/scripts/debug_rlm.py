#!/usr/bin/env python3
"""
debug_rlm.py (CLI)
=====================================

Purpose:
    Debug utility to inspect the RLMConfiguration state.
    Verifies path resolution, manifest loading, and environment variable overrides.
    Useful for troubleshooting cache path conflicts.

Usage Examples:
    python plugins/rlm-factory/skills/rlm-curator/scripts/debug_rlm.py

Input Files:
    - plugins/rlm-factory/resources/manifest-index.json
    - .env

Output:
    - Console output (State inspection)

Key Functions:
    - main(): Prints configuration details for 'tool' and 'sanctuary' modes.

Script Dependencies:
    - plugins/rlm-factory/scripts/rlm_config.py
"""
import os
import sys
from pathlib import Path

# Setup path
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Debug Env
# Debug Env

try:
    from rlm_config import RLMConfig
    
    print("\n--- Testing RLMConfig(type='project') ---")
    config = RLMConfig(run_type="project")
    print(f"Config Type: {config.type}")
    print(f"Manifest Path: {config.manifest_path}")
    print(f"Cache Path: {config.cache_path}")
    print(f"Prompt Template Length: {len(config.prompt_template)}")

    print("\n--- Testing RLMConfig.from_profile('plugins') ---")
    config = RLMConfig.from_profile("plugins")
    print(f"Config Type: {config.type}")
    print(f"Manifest Path: {config.manifest_path}")
    print(f"Cache Path: {config.cache_path}")
    
except ImportError as e:
    print(f"Import Error: {e}")
except Exception as e:
    print(f"Error: {e}")
