import sys
import json
from pathlib import Path
from typing import Optional

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[5]
LEARNING_DIR = PROJECT_ROOT / ".agent" / "learning"
PROFILES_PATH = LEARNING_DIR / "vector_profiles.json"


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
        
    def load_manifest(self) -> dict:
        if not self.manifest_path.exists():
            print(f"⚠️  Manifest not found at {self.manifest_path}")
            return {}
        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error reading manifest: {e}")
            return {}
