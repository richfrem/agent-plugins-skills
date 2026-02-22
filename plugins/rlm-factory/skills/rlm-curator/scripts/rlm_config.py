#!/usr/bin/env python3
"""
rlm_config.py (Shared Module)
=====================================

Purpose:
    Centralized configuration and utility logic for the RLM Toolchain.
    Standardized for profile-based configuration (rlm_profiles.json).
"""

import os
import sys
import json
import glob as globmod
import hashlib
from pathlib import Path
from typing import List, Dict, Optional

# Paths standardization
# File is at: plugins/rlm-factory/skills/rlm-curator/scripts/rlm_config.py
# Root is 6 levels up
PROJECT_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_PROFILES_PATH = PROJECT_ROOT / ".agent" / "learning" / "rlm_profiles.json"


class RLMConfig:
    """
    Configuration object for RLM distillation and curation.
    Loads settings from rlm_profiles.json.
    """
    def __init__(
        self, 
        profile_name: str, 
        project_root: Optional[Path] = None
    ):
        self.root = project_root or PROJECT_ROOT
        self.profile_name = profile_name
        
        # Load profile from JSON
        profiles_data = self._load_profiles_json()
        profile = profiles_data.get("profiles", {}).get(profile_name)
        
        if not profile:
            available = list(profiles_data.get("profiles", {}).keys())
            print(f"❌ RLM Profile '{profile_name}' not found. Available: {available}")
            sys.exit(1)
            
        self.description = profile.get("description", f"RLM Cache: {profile_name}")
        self.allowed_suffixes = profile.get("extensions", [".md", ".py"])
        self.llm_model = profile.get("llm_model", "granite3.2:8b")
        
        # Resolve paths relative to root
        manifest_rel = profile.get("manifest")
        cache_rel = profile.get("cache")
        
        if not manifest_rel or not cache_rel:
            print(f"❌ Profile '{profile_name}' is missing manifest or cache path.")
            sys.exit(1)
            
        self.manifest_path = (self.root / manifest_rel).resolve()
        self.cache_path = (self.root / cache_rel).resolve()
        
        # Default parser and prompt (can be extended in profiles later)
        self.parser_type = profile.get("parser", "directory_glob")
        
        # Prompt loading logic (fallback to legacy default if not in profile)
        prompt_path = profile.get("prompt_path", "plugins/rlm-factory/resources/prompts/rlm/rlm_summarize_legacy.md")
        self.prompt_full_path = (self.root / prompt_path).resolve()
        self.prompt_template = ""
        
        if self.prompt_full_path.exists():
            self.prompt_template = self.prompt_full_path.read_text(encoding="utf-8")
        else:
            # Try internal resource path as fallback
            internal_fall = Path(__file__).resolve().parents[2] / "resources" / "prompts" / "rlm" / "rlm_summarize_legacy.md"
            if internal_fall.exists():
                self.prompt_template = internal_fall.read_text(encoding="utf-8")
        
        # Load Manifest Content
        self.include_patterns = []
        self.exclude_patterns = []
        self._load_manifest_content()

    def _load_profiles_json(self) -> dict:
        if not DEFAULT_PROFILES_PATH.exists():
            return {}
        try:
            with open(DEFAULT_PROFILES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error reading profiles JSON: {e}")
            return {}

    def _load_manifest_content(self):
        if not self.manifest_path.exists():
            print(f"⚠️ Manifest not found: {self.manifest_path}")
            return
        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.include_patterns = data.get("include", [])
                self.exclude_patterns = data.get("exclude", [])
                # Recursive flag is used in file collection
                self.recursive = data.get("recursive", True)
        except Exception as e:
            print(f"⚠️ Error reading manifest {self.manifest_path}: {e}")

    @classmethod
    def from_profile(cls, profile_name: str, project_root: Optional[Path] = None):
        """Standard entry point for profile-based config."""
        return cls(profile_name, project_root)


# ============================================================
# SHARED UTILITIES
# ============================================================

def compute_hash(content: str) -> str:
    """Compute SHA256 hash of file content."""
    return hashlib.sha256(content.encode()).hexdigest()[:16]

def load_cache(cache_path: Path) -> Dict:
    """Load existing cache or return empty dict."""
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading cache at {cache_path}: {e}")
    return {}

def save_cache(cache: Dict, cache_path: Path):
    """Persist cache to disk."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, sort_keys=True)
        f.write("\n")

def should_skip(file_path: Path, config: RLMConfig) -> bool:
    """Check if file should be excluded based on manifest patterns and extensions."""
    path_str = str(file_path.resolve())
    
    # 1. Exclude patterns
    for pattern in config.exclude_patterns:
        if pattern in path_str:
            return True
            
    # 2. Extension check
    if config.allowed_suffixes:
        if file_path.suffix.lower() not in config.allowed_suffixes:
            return True
            
    return False

def collect_files(config: RLMConfig) -> List[Path]:
    """Collect eligible files from PROJECT_ROOT based on manifest include patterns."""
    all_files = []
    root = config.root
    
    for pattern in config.include_patterns:
        # Normalize pattern
        pattern_norm = pattern.replace("\\", "/")
        
        # Use glob for the pattern
        if "*" in pattern_norm or "?" in pattern_norm:
            matches = list(root.glob(pattern_norm))
        else:
            path = root / pattern_norm
            if not path.exists():
                continue
            if path.is_file():
                matches = [path]
            else:
                # Dir: get all files with allowed extensions
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
