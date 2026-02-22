#!/usr/bin/env python3
"""
path_resolver.py (CLI)
=====================================

Purpose:
    Standardizes cross-platform path resolution and provides access to the Master Object Collection.

Layer: Curate / Bundler

Usage Examples:
    python plugins/context-bundler/scripts/path_resolver.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - resolve_root(): Helper: Returns project root.
    - resolve_path(): Helper: Resolves a relative path to absolute.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import json
from typing import Optional, Dict, Any

class PathResolver:
    """
    Static utility class for path resolution and artifact lookup.
    """
    _project_root: Optional[str] = None
    _master_collection: Optional[Dict[str, Any]] = None

    @classmethod
    def get_project_root(cls) -> str:
        """
        Determines the absolute path to the Project Root directory.
        
        Strategy:
        1. Check `PROJECT_ROOT` environment variable.
        2. Traverse parents looking for `legacy-system` or `.agent` directories.
        3. Fallback to CWD if landmarks are missing.

        Returns:
            str: Absolute path to the project root.
        """
        if cls._project_root:
            return cls._project_root

        # 1. Check Env
        if "PROJECT_ROOT" in os.environ:
            cls._project_root = os.environ["PROJECT_ROOT"]
            return cls._project_root

        # 2. Heuristic: Find 'legacy-system' or '.agent' in parents
        current = os.path.abspath(os.getcwd())
        while True:
            if os.path.exists(os.path.join(current, "legacy-system")) or \
               os.path.exists(os.path.join(current, ".agent")):
                cls._project_root = current
                return current
            
            parent = os.path.dirname(current)
            if parent == current: # Reached drive root
                # Fallback to CWD if completely lost
                return os.getcwd()
            current = parent

    @classmethod
    def to_absolute(cls, relative_path: str) -> str:
        """
        Converts a project-relative path to an absolute system path.
        
        Args:
            relative_path (str): Path relative to repo root (e.g., 'plugins/cli.py').
            
        Returns:
            str: Absolute system path (using OS-specific separators).
        """
        root = cls.get_project_root()
        # Handle forward slashes from JSON
        normalized = relative_path.replace("/", os.sep).replace("\\", os.sep)
        return os.path.join(root, normalized)

    @classmethod
    def load_master_collection(cls) -> Dict[str, Any]:
        """
        Loads the master_object_collection.json file into memory (cached).
        
        Returns:
            Dict[str, Any]: The loaded JSON content or an empty dict structure on failure.
        """
        if cls._master_collection:
            return cls._master_collection

        root = cls.get_project_root()
        path = os.path.join(root, "legacy-system", "reference-data", "master_object_collection.json")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                cls._master_collection = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Master Object Collection not found at {path}")
            cls._master_collection = {"objects": {}}
            
        return cls._master_collection

    @classmethod
    def get_object_path(cls, object_id: str, artifact_type: str = "xml") -> Optional[str]:
        """
        Resolves the absolute path for a specific object and artifact type using the Master Collection.
        
        Args:
            object_id (str): The ID (e.g., 'JCSE0086').
            artifact_type (str): The artifact key (e.g., 'xml', 'source', 'sql').
            
        Returns:
            Optional[str]: Absolute path to the file, or None if not found/mapped.
        """
        collection = cls.load_master_collection()
        objects = collection.get("objects", {})
        
        obj_data = objects.get(object_id.upper())
        if not obj_data:
            return None
            
        artifacts = obj_data.get("artifacts", {})
        rel_path = artifacts.get(artifact_type)
        
        if rel_path:
            return cls.to_absolute(rel_path)
            
        return None

# Singleton-like usage helpers
def resolve_root() -> str:
    """Helper: Returns project root."""
    return PathResolver.get_project_root()

def resolve_path(relative_path: str) -> str:
    """Helper: Resolves a relative path to absolute."""
    return PathResolver.to_absolute(relative_path)