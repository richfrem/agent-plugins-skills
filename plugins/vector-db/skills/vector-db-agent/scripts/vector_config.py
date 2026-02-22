import sys
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List


# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[5]
LEARNING_DIR = PROJECT_ROOT / ".agent" / "learning"
PROFILES_PATH = LEARNING_DIR / "vector_profiles.json"

# Default file extensions to index
DEFAULT_EXTENSIONS = [".md", ".txt", ".py", ".json", ".yaml", ".yml", ".sql", ".xml"]


class Manifest:
    """
    Wraps the raw manifest JSON dict and provides file discovery methods.
    Walks `include` directories, filters by `extensions`, and respects `exclude` patterns.
    """
    def __init__(self, data: dict, project_root: Path):
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
        return sorted(set(results))

    def get_files_in_folder(self, folder: str) -> List[str]:
        """Get files within a specific subfolder, respecting extensions and excludes."""
        folder_path = self.project_root / folder
        if not folder_path.exists():
            print(f"⚠️  Folder not found: {folder_path}")
            return []
        results = []
        for ext in self.extensions:
            for f in folder_path.rglob(f"*{ext}"):
                if not f.is_file():
                    continue
                rel = str(f.relative_to(self.project_root))
                if not self._is_excluded(rel):
                    results.append(rel)
        return sorted(set(results))

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

    def get(self, key: str, default=None):
        """Dict-like access for backward compatibility."""
        return self.data.get(key, default)


class VectorConfig:
    """
    Profile-based configuration for the Vector DB plugin.
    Reads all settings from .agent/learning/vector_profiles.json.
    No .env dependency — fully self-contained.
    """
    def __init__(self, profile_name: Optional[str] = None, project_root: Optional[str] = None):
        if project_root:
            self.project_root = Path(project_root)
        else:
            self.project_root = PROJECT_ROOT
        
        # Resolve profiles path relative to project_root (supports custom roots)
        profiles_path = self.project_root / ".agent" / "learning" / "vector_profiles.json"
        
        if not profiles_path.exists():
            print(f"❌ Error: Vector profiles not found at {profiles_path}")
            print(f"   Run: python3 plugins/vector-db/skills/vector-db-init/scripts/init.py")
            sys.exit(1)
            
        try:
            with open(profiles_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ Error reading vector profiles: {e}")
            sys.exit(1)
            
        profiles = data.get("profiles", {})
        
        target_profile = profile_name
        if not target_profile:
            target_profile = data.get("default_profile")
            
        if not target_profile or target_profile not in profiles:
            available = list(profiles.keys()) if profiles else ["(none found)"]
            print(f"❌ Profile '{target_profile}' not found. Available: {available}")
            sys.exit(1)
            
        profile = profiles[target_profile]
        
        self.profile_name = target_profile
        self.description = profile.get("description", "")
        
        # Manifest path
        manifest_raw = profile.get("manifest")
        if not manifest_raw:
            print(f"❌ Profile '{target_profile}' missing 'manifest' path.")
            sys.exit(1)
        self.manifest_path = Path(manifest_raw) if Path(manifest_raw).is_absolute() else self.project_root / manifest_raw
        
        # Collection names
        self.child_collection = profile.get("child_collection", "knowledge_child_v5")
        self.parent_collection = profile.get("parent_collection", "knowledge_parent_v5")
        
        # Connection settings (new — replaces .env vars)
        self.chroma_host = profile.get("chroma_host", "")
        self.chroma_port = int(profile.get("chroma_port", 8110))
        self.chroma_data_path = profile.get("chroma_data_path", ".vector_data")
        
    def load_manifest(self) -> "Manifest":
        """Load and return a Manifest object wrapping the manifest JSON."""
        if not self.manifest_path.exists():
            print(f"⚠️  Manifest not found at {self.manifest_path}")
            return Manifest({}, self.project_root)
        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Manifest(data, self.project_root)
        except Exception as e:
            print(f"⚠️  Error reading manifest: {e}")
            return Manifest({}, self.project_root)

