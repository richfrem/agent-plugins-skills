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
        self.llm_model = profile.get("llm_model", "granite3.2:8b")

        # Resolve all paths relative to project root
        manifest_rel = profile.get("manifest")
        cache_rel = profile.get("cache")

        if not manifest_rel or not cache_rel:
            print(f"[ERROR] Profile '{profile_name}' is missing 'manifest' or 'cache' path.")
            sys.exit(1)

        self.manifest_path = (self.root / manifest_rel).resolve()
        self.cache_path = (self.root / cache_rel).resolve()

        # Parser type and prompt configuration
        self.parser_type = profile.get("parser", "directory_glob")
        prompt_path_rel = profile.get(
            "prompt_path",
            "../assets/resources/prompts/rlm/rlm_summarize_general.md"
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
            print(f"[WARN] Error reading profiles JSON: {e}")
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
            Path(__file__).resolve().parents[1]
            / "resources" / "prompts" / "rlm" / "rlm_summarize_general.md"
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
            print(f"[WARN] Manifest not found: {self.manifest_path}")
            return
        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.include_patterns = data.get("include", [])
            self.exclude_patterns = data.get("exclude", [])
            self.recursive = data.get("recursive", True)
        except Exception as e:
            print(f"[WARN] Error reading manifest {self.manifest_path}: {e}")

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
# load_cache / save_cache — Markdown + YAML persistence
# ----------------------------------------------------------
def _parse_md_cache(filepath: Path) -> Dict:
    """Helper to parse YAML frontmatter and summary from an RLM markdown file."""
    try:
        text = filepath.read_text(encoding="utf-8")
        if text.startswith("---\n"):
            parts = text.split("\n---", 1)
            if len(parts) == 2:
                frontmatter = parts[0].replace("---\n", "")
                summary_block = parts[1].strip()
                summary = summary_block.replace("# Summary\n", "").replace("# Summary", "").strip()
                
                entry = {"summary": summary}
                for line in frontmatter.strip().split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        entry[k.strip()] = v.strip().strip('"').strip("'")
                return entry
    except Exception:
        pass
    return {}

def load_cache(cache_path: Path) -> Dict:
    """
    Load the cache from the Markdown file system database.
    Keys preserve the source file extension (e.g. 'path/to/file.md')
    so they match the output of collect_files() exactly.
    Performs on-the-fly migration if legacy JSON exists.
    """
    cache_dir = cache_path.with_suffix('')  # e.g., rlm_cache_project/
    result = {}

    # 1. Load from the native Markdown hierarchy
    # Each .md file in the cache dir represents ONE source file.
    # The cache file path mirrors the source: source/path/file.md => cache_dir/source/path/file.md
    # So the cache key = the relative path from cache_dir, keeping the .md extension.
    if cache_dir.exists() and cache_dir.is_dir():
        for md_file in cache_dir.rglob("*.md"):
            # Key = path relative to cache dir, forward-slash normalized, with .md preserved
            rel_path = str(md_file.relative_to(cache_dir)).replace("\\", "/")
            entry = _parse_md_cache(md_file)
            if entry:
                result[rel_path] = entry

    # 2. Legacy Migration: Also load from old JSON if it exists
    if cache_path.exists() and cache_path.is_file():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                legacy = json.load(f)
                for k, v in legacy.items():
                    # Normalize old keys: add .md if missing (old format stored without extension)
                    norm_k = k.replace("\\", "/")
                    if not norm_k.endswith(".md"):
                        norm_k = norm_k + ".md"
                    if norm_k not in result:
                        result[norm_k] = v
        except Exception:
            pass

    return result

def save_cache(cache: Dict, cache_path: Path) -> None:
    """
    Persist the cache dict as individual Markdown files, matching the source 
    directory structure underneath the cache directory.
    """
    cache_dir = cache_path.with_suffix('')
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Distribute cache entries to their individual .md files
    for rel_path, entry in cache.items():
        # Strip existing .md suffix to avoid double extension (e.g. decision.md.md)
        rel_path_clean = rel_path[:-3] if rel_path.endswith(".md") else rel_path
        md_file = cache_dir / f"{rel_path_clean}.md"
        md_file.parent.mkdir(parents=True, exist_ok=True)
        
        lines = ["---"]
        for k, v in entry.items():
            if k != "summary":
                val = str(v).replace('"', "'")
                lines.append(f'{k}: "{val}"')
        lines.append("---")
        lines.append("")
        lines.append("# Summary")
        lines.append(str(entry.get("summary", "")))
        lines.append("")
        
        md_file.write_text("\n".join(lines), encoding="utf-8")
        
    # 2. Prune orphan .md files (entries deleted from cache dict by cleanup scripts)
    for md_file in list(cache_dir.rglob("*.md")):
        rel_path = str(md_file.relative_to(cache_dir)).replace("\\", "/")
        if rel_path not in cache:
            md_file.unlink()
            # Clean up empty parent directories
            p = md_file.parent
            while p != cache_dir and not any(p.iterdir()):
                p.rmdir()
                p = p.parent


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
