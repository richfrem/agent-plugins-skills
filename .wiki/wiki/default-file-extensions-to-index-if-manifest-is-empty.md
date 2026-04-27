---
concept: default-file-extensions-to-index-if-manifest-is-empty
source: plugin-code
source_file: vector-db/scripts/vector_config.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.433038+00:00
cluster: self
content_hash: 3f03c9a1c9e449df
---

# Default file extensions to index if manifest is empty

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
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
    
    Loads all settings from vector_profiles.json. This class is 

*(content truncated)*

## See Also

- [[fallback-to-appending-directly-if-kernel-is-missing]]
- [[ensure-unicode-output-works-on-windows-terminals-that-default-to-cp1252]]
- [[file-manifest]]
- [[file-manifest-schema]]
- [[manifest-index]]
- [[part-0-is-empty-part-1-is-yaml]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `vector-db/scripts/vector_config.py`
- **Indexed:** 2026-04-27T05:21:04.433038+00:00
