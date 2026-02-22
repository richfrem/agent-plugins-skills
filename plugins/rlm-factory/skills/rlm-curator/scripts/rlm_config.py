#!/usr/bin/env python3
"""
rlm_config.py (Shared Module)
=====================================

Purpose:
    Centralized configuration and utility logic for the RLM Toolchain.
    Implement the "Manifest Factory" pattern (ADR-0024) to dynamically
    resolve manifests and cache files based on the Analysis Type (Legacy vs Tool).

    This module is the Single Source of Truth for RLM logic.

Layer: Curate / Rlm

Supported Object Types:
    - RLM Config (Legacy Documentation)
    - RLM Config (Tool Discovery)

CLI Arguments (Consumed by Scripts):
    --type  : [legacy|tool] Selects the configuration profile.

Usage Examples:
    # No direct usage (Shared Module)

Input Files:
    - plugins/rlm-factory/resources/manifest-index.json
    - (Manifests referenced by the index)

Output:
    - RLMConfig object (Typed configuration)
    - Shared Utility Pointers (load_cache, save_cache, etc.)

Key Classes/Functions:
    - RLMConfig: Loads and validates configuration from the factory index.
    - load_cache(): Shared cache loader.
    - save_cache(): Shared cache persister.
    - collect_files(): Centralized file discovery logic (Glob vs Inventory).

Script Dependencies:
    - None (this is a dependency for others)

Consumed by:
    - plugins/rlm-factory/scripts/distiller.py
    - plugins/rlm-factory/scripts/query_cache.py
    - plugins/rlm-factory/scripts/cleanup_cache.py
"""
import os
import sys
import json
import glob as globmod
import re
from pathlib import Path

# ============================================================
# CONSTANTS & PROMPTS
# ============================================================

current_dir = Path(__file__).parent.resolve()

def find_project_root(start_path: Path) -> Path:
    """Heuristic to find the project root containing .git or .agent."""
    curr = start_path
    for _ in range(8):  # Max depth to search
        if (curr / ".git").exists() or (curr.joinpath(".agent", "learning")).exists():
            return curr
        if curr.parent == curr:
            break
        curr = curr.parent
    # Fallback if not found (e.g. not in a git repo)
    return current_dir.parents[4] if "skills" in str(current_dir) else current_dir.parents[2]

PROJECT_ROOT = find_project_root(current_dir)


def load_dotenv_file(project_root: Path) -> dict:
    """Parse a .env file into a dict. Used for simple overrides (OLLAMA_MODEL, etc.)."""
    env_path = project_root / ".env"
    env_vars = {}
    if not env_path.exists():
        return env_vars
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    env_vars[key] = value
    except Exception:
        pass
    return env_vars


# Well-known path for the profiles config
DEFAULT_PROFILES_PATH = ".agent/learning/rlm_profiles.json"


def load_profiles_json(project_root: Path) -> dict:
    """Load the RLM profiles config from rlm_profiles.json.
    
    Looks in:
      1. RLM_PROFILES env var or .env value (custom path)
      2. .agent/learning/rlm_profiles.json (well-known default)
    
    Returns the full JSON dict, or empty dict if not found.
    """
    # Check for custom path override
    env_vars = load_dotenv_file(project_root)
    profiles_path_raw = os.getenv("RLM_PROFILES") or env_vars.get("RLM_PROFILES") or DEFAULT_PROFILES_PATH
    
    profiles_path = Path(profiles_path_raw)
    if not profiles_path.is_absolute():
        profiles_path = project_root / profiles_path_raw
    
    if not profiles_path.exists():
        return {}
    
    try:
        with open(profiles_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Error reading profiles JSON: {e}")
        return {}


def discover_profiles(project_root: Path) -> dict:
    """Discover all RLM cache profiles from rlm_profiles.json.
    
    Returns dict of profile_name -> {description, manifest, cache, extensions}.
    """
    data = load_profiles_json(project_root)
    return data.get("profiles", {})

def find_factory_index(script_dir: Path) -> Path:
    """Find manifest-index.json in local or parent resources/."""
    # Option 1: script_dir/resources/ (Flat structure like tools/name/)
    opt1 = script_dir / "resources" / "manifest-index.json"
    if opt1.exists():
        return opt1
    # Option 2: script_dir/../resources/ (Plugin structure like plugins/name/scripts/)
    opt2 = script_dir.parent / "resources" / "manifest-index.json"
    if opt2.exists():
        return opt2
    # Option 3: script_dir/../../resources/ (Skill structure like plugins/name/skills/skill-name/scripts/)
    opt3 = script_dir.parent.parent / "resources" / "manifest-index.json"
    if opt3.exists():
        return opt3
    # Option 4: script_dir/../../../resources/ (Deep Skill structure like plugins/name/skills/skill-name/scripts/)
    opt4 = script_dir.parent.parent.parent / "resources" / "manifest-index.json"
    if opt4.exists():
        return opt4
    # Default to current_dir / resources (will error gracefully if not found)
    return opt1

FACTORY_INDEX_PATH = find_factory_index(current_dir)

class RLMConfig:
    def __init__(self, run_type="project", override_targets=None):
        self.type = run_type
        self.manifest_data = {}
        self.cache_path = None
        self.parser_type = "directory_glob"
        self.prompt_template = "" # Loaded dynamically
        self.targets = []
        self.exclude_patterns = []
        self.allowed_suffixes = []
        
        # Load Factory Index
        if not FACTORY_INDEX_PATH.exists():
            print(f"❌ Factory Index not found at {FACTORY_INDEX_PATH}")
            sys.exit(1)
            
        try:
            with open(FACTORY_INDEX_PATH, "r") as f:
                factory_index = json.load(f)
        except Exception as e:
            print(f"❌ Invalid Factory Index JSON: {e}")
            sys.exit(1)
            
        # Resolve Config Definition
        config_def = factory_index.get(run_type)

        if not config_def:
            print(f"❌ Unknown RLM Type: '{run_type}'. Available: {list(factory_index.keys())}")
            sys.exit(1)

        self.description = config_def.get("description", "RLM Configuration")
        self.allowed_suffixes = config_def.get("allowed_suffixes", [".md", ".txt"])
            
        # Resolve Paths
        # Manifest is relative to Project Root (Standardized)
        manifest_path_raw = config_def["manifest"]
        self.manifest_path = (PROJECT_ROOT / manifest_path_raw).resolve()
        
        # Cache Path Resolution (Env Overrides Manifest)
        # Dedicated to General Cache for rlm-factory plugin
        env_prefix = config_def.get("env_prefix", "RLM_SUMMARY")
        env_cache_path = os.getenv(f"{env_prefix}_CACHE")
        
        if env_cache_path:
             # If absolute, use as is. If relative, resolve from Project Root.
             self.cache_path = Path(env_cache_path)
             if not self.cache_path.is_absolute():
                   self.cache_path = PROJECT_ROOT / env_cache_path
        else:
             # Fallback to manifest default
             cache_path_raw = config_def["cache"]
             self.cache_path = PROJECT_ROOT / cache_path_raw
            
        self.parser_type = config_def.get("parser", "directory_glob")
        
        # Load LLM Model (Env > Manifest > Default)
        self.llm_model = os.getenv("OLLAMA_MODEL") or config_def.get("llm_model") or "granite3.2:8b"
        
        # Load Prompt from Path (Relative to Project Root)
        prompt_rel_path = config_def.get("prompt_path")
        if prompt_rel_path:
            # Resolve relative to Project Root
            prompt_full_path = (PROJECT_ROOT / prompt_rel_path).resolve()
            if prompt_full_path.exists():
                try:
                    self.prompt_template = prompt_full_path.read_text(encoding="utf-8")
                except Exception as e:
                    print(f"⚠️  Error reading prompt file {prompt_full_path}: {e}")
            else:
                print(f"⚠️  Prompt file not found: {prompt_full_path}")
        else:
            print("⚠️  No 'prompt_path' defined in configuration.")
            
        # Fallback if loading failed
        if not self.prompt_template:
            print(f"❌ Critical Error: Failed to load prompt template for type '{run_type}'.")
            sys.exit(1)
        
        # Load the actual Manifest
        self.load_manifest_content()
        
        if override_targets:
            self.targets = override_targets

    @classmethod
    def from_profile(cls, profile_name, project_root=None):
        """Create an RLMConfig from a rlm_profiles.json profile.
        
        This bypasses the factory index entirely and reads config from JSON.
        """
        root = project_root or PROJECT_ROOT
        profiles = discover_profiles(root)
        
        if profile_name not in profiles:
            available = list(profiles.keys()) if profiles else ["(none found)"]
            print(f"❌ Profile '{profile_name}' not found in rlm_profiles.json. Available: {available}")
            sys.exit(1)
        
        profile = profiles[profile_name]
        
        config = cls.__new__(cls)
        config.type = profile_name
        config.description = f"RLM Cache: {profile_name}"
        config.manifest_data = {}
        config.parser_type = "directory_glob"
        config.prompt_template = ""  # Not needed for audit
        config.targets = []
        config.exclude_patterns = []
        config.allowed_suffixes = profile["extensions"]
        config.llm_model = os.getenv("OLLAMA_MODEL") or profile.get("llm_model") or "granite3.2:8b"
        # Resolve manifest path
        manifest_raw = profile["manifest"]
        config.manifest_path = Path(manifest_raw) if Path(manifest_raw).is_absolute() else root / manifest_raw
        
        # Resolve cache path
        cache_raw = profile["cache"]
        config.cache_path = Path(cache_raw) if Path(cache_raw).is_absolute() else root / cache_raw
        
        # Load the manifest
        config.load_manifest_content()
        
        return config  # was missing — from_profile() always returned None without this

    def load_manifest_content(self):
        if not self.manifest_path.exists():
            print(f"⚠️  Manifest not found: {self.manifest_path}")
            return

        try:
            with open(self.manifest_path, "r") as f:
                data = json.load(f)
                
            if self.parser_type == "directory_glob":
                self.targets = data.get("include", [])
                self.exclude_patterns = data.get("exclude", [])
            elif self.parser_type == "inventory_dict":
                self.manifest_data = data
                self.targets = ["INVENTORY_ROOT"]
                self.exclude_patterns = data.get("exclude", [])
                 
        except Exception as e:
            print(f"⚠️  Error reading manifest {self.manifest_path}: {e}")

# ============================================================
# SHARED UTILITIES  (module-level, not inside RLMConfig class)
# ============================================================

import hashlib
from typing import List, Dict

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
            print(f"⚠️  Error loading cache: {e}")
    return {}

def save_cache(cache: Dict, cache_path: Path):
    """Persist cache to disk immediately (crash-resilient)."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, sort_keys=True)

def should_skip(file_path: Path, config: RLMConfig, debug_fn=None) -> bool:
    """Check if file should be excluded from processing."""
    
    def log(msg):
        if debug_fn:
            debug_fn(msg)
            
    try:
        # Canonicalize path for consistent matching
        path_obj = file_path.resolve()
        path_str = str(path_obj)
    except Exception as e:
        print(f"⚠️  SKIP CHECK FAILED (path resolution): {file_path} — {e}")
        return False  # fail-open (do not skip if we can't check)

    # Check exclude patterns
    for pattern in config.exclude_patterns:
        if pattern in path_str:
            log(f"Skipping {path_str} (exclude pattern: {pattern})")
            return True
    
    # Allowed Suffixes Check
    if config.allowed_suffixes:
        if file_path.suffix.lower() not in config.allowed_suffixes:
            log(f"Skipping due to unsupported suffix: {file_path.suffix}")
            return True
    
    return False

def collect_files(config: RLMConfig) -> List[Path]:
    """Collect all eligible files based on parser type."""
    all_files = []
    
    if config.parser_type == "inventory_dict":
        # Recursively search for "path" keys in the JSON inventory
        def recursive_search(data):
            if isinstance(data, dict):
                # Check if this node looks like a tool definition
                if "path" in data and isinstance(data["path"], str):
                    path_str = data["path"]
                    # If relative, resolve from project root
                    if not os.path.isabs(path_str):
                        full_path = (PROJECT_ROOT / path_str).resolve()
                    else:
                        full_path = Path(path_str)
                    
                    if full_path.exists():
                        if full_path.is_file():
                            if not should_skip(full_path, config):
                                all_files.append(full_path)
                        elif full_path.is_dir():
                            for ext in config.allowed_suffixes:
                                for f in full_path.glob(f"**/*{ext}"):
                                    if f.is_file() and not should_skip(f, config):
                                        all_files.append(f)
                
                # Recurse into values
                for v in data.values():
                    recursive_search(v)
            
            elif isinstance(data, list):
    return hashlib.sha256(content.encode()).hexdigest()[:16]

def load_cache(cache_path: Path) -> Dict:
    """Load existing cache or return empty dict."""
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading cache: {e}")
    return {}

def save_cache(cache: Dict, cache_path: Path):
    """Persist cache to disk immediately (crash-resilient)."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, sort_keys=True)

def should_skip(file_path: Path, config: "RLMConfig", debug_fn=None) -> bool:
    """Check if file should be excluded from processing."""
    
    def log(msg):
        if debug_fn:
            debug_fn(msg)
            
    try:
        # Canonicalize path for consistent matching
        path_obj = file_path.resolve()
        path_str = str(path_obj)
    except Exception as e:
        print(f"⚠️  SKIP CHECK FAILED (path resolution): {file_path} — {e}")
        return False  # fail-open (do not skip if we can't check)

    # Check exclude patterns
    for pattern in config.exclude_patterns:
        if pattern in path_str:
            log(f"Skipping {path_str} (exclude pattern: {pattern})")
            return True
    
    # Allowed Suffixes Check
    if config.allowed_suffixes:
        if file_path.suffix.lower() not in config.allowed_suffixes:
            log(f"Skipping due to unsupported suffix: {file_path.suffix}")
            return True
    
    return False

def collect_files(config: "RLMConfig") -> List[Path]:
    """Collect all eligible files based on parser type."""
    all_files = []
    
    if config.parser_type == "inventory_dict":
        # Recursively search for "path" keys in the JSON inventory
        def recursive_search(data):
            if isinstance(data, dict):
                # Check if this node looks like a tool definition
                if "path" in data and isinstance(data["path"], str):
                    path_str = data["path"]
                    # If relative, resolve from project root
                    if not os.path.isabs(path_str):
                        full_path = (PROJECT_ROOT / path_str).resolve()
                    else:
                        full_path = Path(path_str)
                    
                    if full_path.exists():
                        if full_path.is_file():
                            if not should_skip(full_path, config):
                                all_files.append(full_path)
                        elif full_path.is_dir():
                            for ext in config.allowed_suffixes:
                                for f in full_path.glob(f"**/*{ext}"):
                                    if f.is_file() and not should_skip(f, config):
                                        all_files.append(f)
                
                # Recurse into values
                for v in data.values():
                    recursive_search(v)
            
            elif isinstance(data, list):
                # Recurse into list items
                for item in data:
                    recursive_search(item)

        recursive_search(config.manifest_data)
        
        # Post-process: Filter by targets if overridden
        if config.targets and "INVENTORY_ROOT" not in config.targets:
             filtered_files = []
             for f in all_files:
                  for t in config.targets:
                       # Normalize
                       t_path = (PROJECT_ROOT / t).resolve()
                       # Check if file is same or inside target dir
                       try:
                           # is_relative_to is Python 3.9+
                           # f.relative_to(t_path)
                           # But explicit check for parents is safer across versions
                           if f == t_path or t_path in f.parents:
                               filtered_files.append(f)
                               break
                       except Exception:
                           pass
             all_files = filtered_files
                    
    elif config.parser_type == "directory_glob":
        # Default Directory Globbing (supports wildcards like plugins/*/README.md)
        for target in config.targets:
            # Normalize path separators for cross-platform compatibility
            target_normalized = target.replace("\\", "/")
            
            # Check if target contains glob wildcards
            if "*" in target_normalized or "?" in target_normalized:
                # Resolve glob from project root
                glob_results = globmod.glob(str(PROJECT_ROOT / target_normalized))
                for match in glob_results:
                    match_path = Path(match)
                    if match_path.is_file():
                        if not should_skip(match_path, config):
                            all_files.append(match_path)
                    elif match_path.is_dir():
                        for ext in config.allowed_suffixes:
                            for f in match_path.glob(f"**/*{ext}"):
                                if f.is_file() and not should_skip(f, config):
                                    all_files.append(f)
                continue
            
            path = PROJECT_ROOT / target_normalized
            
            if not path.exists():
                continue
                
            # If target is file
            if path.is_file():
                if not should_skip(path, config):
                    all_files.append(path)
                continue
                
            # If target is dir
            for ext in config.allowed_suffixes:
                for f in path.glob(f"**/*{ext}"):
                    if f.is_file() and not should_skip(f, config):
                        all_files.append(f)
                        
    return all_files
            

