#!/usr/bin/env python3
"""
rlm_config.py
=====================================

Purpose:
    Centralized configuration and utility logic for the RLM Toolchain.
    Loads profile settings exclusively from `.agent/learning/rlm_profiles.json`,
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
# PATHS
# File is at: plugins/rlm-factory/skills/rlm-curator/scripts/rlm_config.py
# Root is 6 levels up (scripts→rlm-curator→skills→rlm-factory→plugins→ROOT)
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_PROFILES_PATH = PROJECT_ROOT / ".agent" / "learning" / "rlm_profiles.json"


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
            print(f"❌ RLM Profile '{profile_name}' not found. Available: {available}")
            sys.exit(1)

        self.description = profile.get("description", f"RLM Cache: {profile_name}")
        self.allowed_suffixes = profile.get("extensions", [".md", ".py"])
        self.llm_model = profile.get("llm_model", "granite3.2:8b")

        # Resolve all paths relative to project root
        manifest_rel = profile.get("manifest")
        cache_rel = profile.get("cache")

        if not manifest_rel or not cache_rel:
            print(f"❌ Profile '{profile_name}' is missing 'manifest' or 'cache' path.")
            sys.exit(1)

        self.manifest_path = (self.root / manifest_rel).resolve()
        self.cache_path = (self.root / cache_rel).resolve()

        # Parser type and prompt configuration
        self.parser_type = profile.get("parser", "directory_glob")
        prompt_path_rel = profile.get(
            "prompt_path",
            "plugins/rlm-factory/resources/prompts/rlm/rlm_summarize_legacy.md"
        )
        self.prompt_full_path = (self.root / prompt_path_rel).resolve()
        self.prompt_template = self._load_prompt()

        # File collection patterns (populated from manifest)
        self.include_patterns: List[str] = []
        self.exclude_patterns: List[str] = []
        self.recursive: bool = True
        self._load_manifest_content()

    # ----------------------------------------------------------
    # Private helpers
    # ----------------------------------------------------------

    def _load_profiles_json(self) -> dict:
        """
        Load the raw rlm_profiles.json data from disk.

        Returns:
            Parsed JSON as a dict, or empty dict on failure.
        """
        if not DEFAULT_PROFILES_PATH.exists():
            return {}
        try:
            with open(DEFAULT_PROFILES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error reading profiles JSON: {e}")
            return {}

    def _load_prompt(self) -> str:
        """
        Load the prompt template from the configured path, with a fallback.

        Returns:
            Prompt template string, or empty string if not found.
        """
        if self.prompt_full_path.exists():
            return self.prompt_full_path.read_text(encoding="utf-8")

        # Fallback: check relative to the skill's resources directory
        internal_fallback = (
            Path(__file__).resolve().parents[2]
            / "resources" / "prompts" / "rlm" / "rlm_summarize_legacy.md"
        )
        if internal_fallback.exists():
            return internal_fallback.read_text(encoding="utf-8")

        return ""

    def _load_manifest_content(self) -> None:
        """
        Populate include/exclude patterns from the manifest JSON file.
        Logs a warning if the manifest does not exist.
        """
        if not self.manifest_path.exists():
            print(f"⚠️ Manifest not found: {self.manifest_path}")
            return
        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.include_patterns = data.get("include", [])
            self.exclude_patterns = data.get("exclude", [])
            self.recursive = data.get("recursive", True)
        except Exception as e:
            print(f"⚠️ Error reading manifest {self.manifest_path}: {e}")

    @classmethod
    def from_profile(cls, profile_name: str, project_root: Optional[Path] = None) -> "RLMConfig":
        """
        Standard factory entry point for profile-based config.

        Args:
            profile_name: Name of the profile to load.
            project_root: Optional override for the project root path.

        Returns:
            Initialized RLMConfig instance.
        """
        return cls(profile_name, project_root)


# ============================================================
# SHARED UTILITIES
# ============================================================

# ----------------------------------------------------------
# compute_hash — content fingerprinting for cache freshness
# ----------------------------------------------------------
def compute_hash(content: str) -> str:
    """
    Compute a short SHA256 hash of the file content.

    Args:
        content: Raw file content string.

    Returns:
        First 16 characters of the SHA256 hex digest.
    """
    return hashlib.sha256(content.encode()).hexdigest()[:16]


# ----------------------------------------------------------
# load_cache / save_cache — crash-resilient JSON persistence
# ----------------------------------------------------------
def load_cache(cache_path: Path) -> Dict:
    """
    Load the cache JSON from disk.

    Args:
        cache_path: Path to the cache JSON file.

    Returns:
        Parsed cache dict, or empty dict if the file doesn't exist or is invalid.
    """
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading cache at {cache_path}: {e}")
    return {}


def save_cache(cache: Dict, cache_path: Path) -> None:
    """
    Persist the cache dict to disk, creating parent directories as needed.

    Args:
        cache: Cache data to serialize.
        cache_path: Target path for the JSON file.
    """
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, sort_keys=True)
        f.write("\n")


# ----------------------------------------------------------
# should_skip — file exclusion predicate
# ----------------------------------------------------------
def should_skip(file_path: Path, config: RLMConfig) -> bool:
    """
    Determine whether a file should be excluded from processing.

    Checks both the exclude pattern list (substring match on absolute path)
    and the allowed suffix list.

    Args:
        file_path: Absolute path to the file.
        config: Active RLMConfig instance.

    Returns:
        True if the file should be skipped, False otherwise.
    """
    path_str = str(file_path.resolve())

    # 1. Exclude patterns (substring match)
    for pattern in config.exclude_patterns:
        if pattern in path_str:
            return True

    # 2. Extension allowlist
    if config.allowed_suffixes:
        if file_path.suffix.lower() not in config.allowed_suffixes:
            return True

    return False


# ----------------------------------------------------------
# collect_files — manifest-driven file discovery
# ----------------------------------------------------------
def collect_files(config: RLMConfig) -> List[Path]:
    """
    Collect eligible files from the project root based on manifest include patterns.

    Supports glob wildcards (e.g. `plugins/*/README.md`) and directory targets.
    Files are deduplicated and returned in sorted order.

    Args:
        config: Active RLMConfig instance providing include patterns and filters.

    Returns:
        Sorted, deduplicated list of absolute Path objects.
    """
    all_files: List[Path] = []
    root = config.root

    for pattern in config.include_patterns:
        pattern_norm = pattern.replace("\\", "/")

        if "*" in pattern_norm or "?" in pattern_norm:
            # Glob pattern — resolve from root
            matches = list(root.glob(pattern_norm))
        else:
            path = root / pattern_norm
            if not path.exists():
                continue
            if path.is_file():
                matches = [path]
            else:
                # Directory target — scan for all allowed extensions
                matches = []
                for ext in config.allowed_suffixes:
                    if config.recursive:
                        matches.extend(path.glob(f"**/*{ext}"))
                    else:
                        matches.extend(path.glob(f"*{ext}"))

        for match in matches:
            if match.is_file() and not should_skip(match, config):
                all_files.append(match)

    return sorted(list(set(all_files)))
