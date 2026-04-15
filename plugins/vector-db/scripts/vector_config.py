#!/usr/bin/env python3
"""
vector_config.py
=====================================

Purpose:
    Profile-based configuration loader for the Vector DB plugin.
    Reads all operational parameters (batch size, model name, chunking) 
    exclusively from vector_profiles.json.

Layer: Curate / Retrieve

Usage:
    from vector_config import VectorConfig
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Default file extensions to index if manifest is empty
DEFAULT_EXTENSIONS = [".md", ".txt", ".py", ".json", ".yaml", ".yml", ".sql", ".xml"]

def _find_project_root(start_path: Path) -> Path:
    """Walks up from start_path to find the first directory containing .git."""
    current = start_path.resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").is_dir():
            return parent
    return current.parents[2]

PROJECT_ROOT = _find_project_root(Path(__file__))


class Manifest:
    """
    Wraps the raw manifest JSON dict and provides file discovery methods.
    """

    def __init__(self, data: Dict[str, Any], project_root: Path) -> None:
        """
        Initialize the Manifest.

        Args:
            data: Parsed JSON dictionary.
            project_root: Root path of the project.
        """
        self.data = data
        self.project_root = project_root
        self.include_dirs: List[str] = data.get("include", [])
        self.exclude_patterns: List[str] = data.get("exclude", [])
        self.extensions: List[str] = data.get("extensions", DEFAULT_EXTENSIONS)

    def _is_excluded(self, rel_path: str) -> bool:
        """Check if a relative path matches any exclude pattern."""
        for pattern in self.exclude_patterns:
            if pattern in rel_path:
                return True
        return False

    def get_files(self) -> List[str]:
        """Walk all include directories and return relative file paths."""
        results = []
        for inc_dir in self.include_dirs:
            inc_path = self.project_root / inc_dir
            if not inc_path.exists():
                continue
            if inc_path.is_file():
                rel = str(inc_path.relative_to(self.project_root))
                if not self._is_excluded(rel):
                    results.append(rel)
                continue
            for ext in self.extensions:
                for f in inc_path.rglob(f"*{ext}"):
                    if not f.is_file():
                        continue
                    rel = str(f.relative_to(self.project_root))
                    if not self._is_excluded(rel):
                        results.append(rel)
        return sorted(list(set(results)))

    def get_files_in_folder(self, folder: str) -> List[str]:
        """Get files within a specific subfolder."""
        folder_path = self.project_root / folder
        if not folder_path.exists():
            return []
        results = []
        for ext in self.extensions:
            for f in folder_path.rglob(f"*{ext}"):
                if not f.is_file():
                    continue
                rel = str(f.relative_to(self.project_root))
                if not self._is_excluded(rel):
                    results.append(rel)
        return sorted(list(set(results)))

    def get_files_modified_since(self, cutoff: datetime) -> List[str]:
        """Get files modified after the cutoff datetime."""
        all_files = self.get_files()
        results = []
        cutoff_ts = cutoff.timestamp()
        for rel_path in all_files:
            full_path = self.project_root / rel_path
            try:
                if os.path.getmtime(full_path) >= cutoff_ts:
                    results.append(rel_path)
            except OSError:
                continue
        return results


class VectorConfig:
    """
    Profile-based configuration for the Vector DB plugin.
    
    Loads all settings from vector_profiles.json. This class is the 
    Single Source of Truth for vector configuration.
    """

    def __init__(
        self, 
        profile_name: Optional[str] = None, 
        project_root: Optional[str] = None
    ) -> None:
        """
        Load configuration from the named profile in vector_profiles.json.

        Args:
            profile_name: Name of the profile to use.
            project_root: Optional override for the project root.
        """
        self.project_root = Path(project_root) if project_root else PROJECT_ROOT
        
        profiles_path = self.project_root / ".agent" / "learning" / "vector_profiles.json"
        
        if not profiles_path.exists():
            print(f"[ERROR] Vector profiles not found at {profiles_path}")
            sys.exit(1)
            
        try:
            with open(profiles_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[ERROR] Reading vector profiles: {e}")
            sys.exit(1)
            
        profiles = data.get("profiles", {})
        target_profile = profile_name or data.get("default_profile")
            
        if not target_profile or target_profile not in profiles:
            available = list(profiles.keys()) if profiles else ["(none)"]
            print(f"[ERROR] Profile '{target_profile}' not found. Available: {available}")
            sys.exit(1)
            
        profile = profiles[target_profile]
        
        # Identity & Paths
        self.profile_name = target_profile
        self.description = profile.get("description", "")
        self.child_collection = profile.get("child_collection", "vector_child_v1")
        self.parent_collection = profile.get("parent_collection", "vector_parent_v1")
        
        # Manifest
        manifest_raw = profile.get("manifest")
        if not manifest_raw:
            print(f"[ERROR] Profile '{target_profile}' missing 'manifest' path.")
            sys.exit(1)
        self.manifest_path = self.project_root / manifest_raw
        
        # Connection
        self.chroma_host = profile.get("chroma_host", "")
        self.chroma_port = int(profile.get("chroma_port", 8110))
        self.chroma_data_path = profile.get("chroma_data_path", ".vector_data")
        
        # Operational parameters (Self-Configurable)
        self.batch_size = int(profile.get("batch_size", 100))
        self.embedding_model = profile.get("embedding_model", "nomic-ai/nomic-embed-text-v1.5")
        self.device = profile.get("device", "cpu")
        
        # Chunking parameters
        self.parent_chunk_size = int(profile.get("parent_chunk_size", 2000))
        self.parent_chunk_overlap = int(profile.get("parent_chunk_overlap", 200))
        self.child_chunk_size = int(profile.get("child_chunk_size", 400))
        self.child_chunk_overlap = int(profile.get("child_chunk_overlap", 50))
        
    def load_manifest(self) -> Manifest:
        """Loads and parses the manifest file defined in the profile."""
        if not self.manifest_path.exists():
            return Manifest({}, self.project_root)
        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                return Manifest(json.load(f), self.project_root)
        except Exception as e:
            print(f"[WARN] Error reading manifest: {e}")
            return Manifest({}, self.project_root)
