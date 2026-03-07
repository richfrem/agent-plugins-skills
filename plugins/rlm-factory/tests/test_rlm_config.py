import os
import sys
import json
import pytest
from pathlib import Path

# Add the scripts directory so we can import rlm_config
SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
from rlm_config import RLMConfig, compute_hash, load_cache, save_cache, collect_files

@pytest.fixture
def mock_project(tmp_path):
    """Creates a mock project structure with a profile, manifest, and cache."""
    agent_dir = tmp_path / ".agent" / "learning"
    agent_dir.mkdir(parents=True)
    
    profiles_path = agent_dir / "rlm_profiles.json"
    manifest_path = agent_dir / "test_manifest.json"
    cache_path = agent_dir / "test_cache.json"
    
    # Mock Profiles
    profiles_data = {
        "version": 1,
        "default_profile": "test",
        "profiles": {
            "test": {
                "description": "Test profile",
                "manifest": f".agent/learning/{manifest_path.name}",
                "cache": f".agent/learning/{cache_path.name}",
                "extensions": [".py", ".md"]
            }
        }
    }
    profiles_path.write_text(json.dumps(profiles_data))
    
    # Mock Manifest
    manifest_data = {
        "description": "Test manifest",
        "include": ["src/"],
        "exclude": [".git/", "__pycache__/"],
        "recursive": True
    }
    manifest_path.write_text(json.dumps(manifest_data))
    
    # Mock Cache
    cache_data = {"src/main.py": {"hash": "abc", "summary": "main"}}
    cache_path.write_text(json.dumps(cache_data))
    
    # Set the environment variable to point to our mock profiles
    os.environ["RLM_PROFILES_PATH"] = str(profiles_path)
    
    yield tmp_path
    
    # Cleanup
    if "RLM_PROFILES_PATH" in os.environ:
        del os.environ["RLM_PROFILES_PATH"]


def test_rlm_config_initialization(mock_project, monkeypatch):
    """Test that RLMConfig loads correctly from the mock project."""
    import rlm_config
    monkeypatch.setattr(rlm_config, "PROJECT_ROOT", mock_project)
    
    # Also patch the global default path that got resolved at import time
    mock_profiles = mock_project / ".agent" / "learning" / "rlm_profiles.json"
    monkeypatch.setattr(rlm_config, "DEFAULT_PROFILES_PATH", mock_profiles)
    
    config = RLMConfig("test", project_root=mock_project)
    assert config.profile_name == "test"
    assert config.description == "Test profile"
    assert config.manifest_path.name == "test_manifest.json"
    assert config.cache_path.name == "test_cache.json"
    assert set(config.allowed_suffixes) == set([".py", ".md"])
    assert config.include_patterns == ["src/"]


def test_compute_hash():
    """Test that hashing produces a consistent length output."""
    h1 = compute_hash("Hello, world!")
    h2 = compute_hash("Hello, world!")
    assert h1 == h2
    assert len(h1) == 16


def test_load_save_cache(tmp_path):
    """Test cache persistence functions."""
    cache_path = tmp_path / "test_cache.json"
    data = {"file.py": {"summary": "test"}}
    
    save_cache(data, cache_path)
    loaded = load_cache(cache_path)
    
    assert loaded == data
