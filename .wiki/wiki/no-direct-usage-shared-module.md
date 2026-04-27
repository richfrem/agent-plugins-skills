---
concept: no-direct-usage-shared-module
source: plugin-code
source_file: rlm-factory/scripts/rlm_config.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.342221+00:00
cluster: path
content_hash: f1b924a5176f6671
---

# No direct usage (Shared Module)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/rlm-factory/scripts/rlm_config.py -->
#!/usr/bin/env python
"""
rlm_config.py
=====================================

Purpose:
    Centralized configuration and utility logic for the RLM Toolchain.
    Loads profile settings exclusively from a profiles JSON file (configured via 
    RLM_PROFILES_PATH env var, defaulting to `.agent/learning/rlm_profiles.json`),
    making this module the Single Source of Truth for all RLM operations.

Layer: Curate / Rlm

Usage:
    # No direct usage (Shared Module)
    from rlm_config import RLMConfig, load_cache, save_cache, collect_files

Related:
    - distiller.py
    - query_cache.py
    - cleanup_cache.py
    - inventory.py
"""
import os
import sys
import json
import glob as globmod
import hashlib
from pathlib import Path
from typing import List, Dict, Optional

# ============================================================
# PATHS:
# Robustly discover the Project Root from wherever this script happens
# to be installed (e.g. plugins/ vs .agents/skills/)
# ============================================================
def _find_project_root(start_path: Path) -> Path:
    current = start_path.resolve()
    # 1. Walk up to explicitly find the repository root (looking for .git)
    for parent in [current] + list(current.parents):
        if (parent / ".git").is_dir():
            return parent
            
    # 2. Fallback to older depth assumption if not in a git repo
    return current.parents[3]

PROJECT_ROOT = _find_project_root(Path(__file__))

def _get_profiles_path() -> Path:
    """Get the path to rlm_profiles.json from env var or default."""
    env_path = os.getenv("RLM_PROFILES_PATH")
    if env_path:
        path = Path(env_path)
        return path if path.is_absolute() else (PROJECT_ROOT / path).resolve()
    
    # Try singular first (older spec), then plural (current spec)
    p1 = PROJECT_ROOT / ".agent" / "learning" / "rlm_profiles.json"
    p2 = PROJECT_ROOT / ".agents" / "learning" / "rlm_profiles.json"
    
    if p1.exists():
        return p1
    return p2

DEFAULT_PROFILES_PATH = _get_profiles_path()


class RLMConfig:
    """
    Profile-based configuration for the RLM distillation toolchain.

    Loads all settings from a named profile in `rlm_profiles.json`. This
    class is the single configuration entry point for all RLM scripts.

    Attributes:
        profile_name: Name of the loaded profile.
        root: Resolved project root path.
        manifest_path: Resolved path to the manifest JSON.
        cache_path: Resolved path to the cache JSON.
        include_patterns: Glob patterns to include during file collection.
        exclude_patterns: Substrings to exclude during file collection.
        allowed_suffixes: File extensions to process.
        llm_model: Ollama model name to use for distillation.
        prompt_template: Loaded prompt text for the LLM.
    """

    def __init__(
        self,
        profile_name: str,
        project_root: Optional[Path] = None
    ) -> None:
        """
        Initialize RLMConfig from a named profile.

        Args:
            profile_name: Name of the profile to load from rlm_profiles.json.
            project_root: Optional override for the project root path.

        Raises:
            SystemExit: If the profile is not found or required keys are missing.
        """
        self.root = project_root or PROJECT_ROOT
        self.profile_name = profile_name

        # Load and validate the named profile from JSON
        profiles_data = self._load_profiles_json()
        profile = profiles_data.get("profiles", {}).get(profile_name)

        if not profile:
            available = list(profiles_data.get("profiles", {}).keys())
            print(f"[ERROR] RLM Profile '{profile_name}' not found. Available: {available}")
            sys.exit(1)

        self.description = profile.get("description", f"RLM Cache: {profile_name}")
        self.allowed_suffixes = profile.get("extensions", [".md", ".py"])
        self.llm_model = profile.get("llm_model", "granit

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/rlm-cleanup-agent/scripts/rlm_config.py -->
#!/usr/bin/env python3
"""
rlm_config.py
=====================================

Purpose:
    Centralized configuration and utility logic for the RLM Toolchain.
    Loads profile settings exclusively from a profiles JSON file (configured via 
    RLM_PROFILES_PATH env var, defaulting to `.agent/learning/rlm_profiles.json`),
    making this module the Single Source of Truth for all RLM operations.

Layer: Curate / Rlm

Usage:
    # No direct usage (Shared Module)
    from rlm_config import RLMConfig, load_cache, save_cache, collect_files

Related:
    - distiller.py
    - query_cache.py
    - cleanup_cache.py
    - inventory.py
"""
import os
import sys
import json
import glob as globmod
import hashlib
from pathlib import Path
from typing import List, Dict, Optional

# =================================

*(combined content truncated)*

## See Also

- [[adr-004-self-contained-plugins---no-cross-plugin-script-dependencies]]
- [[agentic-os-operational-guide-usage]]
- [[extract-module-name]]
- [[no-session-in-progress-suggest-starting-one]]
- [[simple-tasks-no---model-flag-defaults-to-freecheap-model-gpt-5-mini-via-copilot]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `rlm-factory/scripts/rlm_config.py`
- **Indexed:** 2026-04-27T05:21:04.342221+00:00
