---
concept: default-discovery-tags-for-llm-retraining-crawlers-override-via-hugging-face-tags-env-var
source: plugin-code
source_file: huggingface-utils/scripts/hf_config.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.243521+00:00
cluster: import
content_hash: b54cf7026964f2bb
---

# Default discovery tags for LLM retraining crawlers — override via HUGGING_FACE_TAGS env var

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/huggingface-utils/scripts/hf_config.py -->
"""
hf_config.py
=====================================

Purpose:
    Single source of truth for HuggingFace credentials, repo IDs, and environment variable resolution.
    All HF-consuming plugins import from here.

Layer: Infrastructure / Configuration

Usage Examples:
    pythonf_config.py

Supported Object Types:
    None

CLI Arguments:
    None

Input Files:
    - .env file for credentials

Output:
    - JSON string printed containing configuration validation status.

Key Functions:
    get_hf_config(): Resolves and returns HFConfig.
    validate_config(): Returns status report of configuration.

Script Dependencies:
    os, sys, json, logging, pathlib, typing, dataclasses

Consumed by:
    - hf-init skill
    - upload.py
"""
import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger("hf_config")

# Default discovery tags for LLM retraining crawlers — override via HUGGING_FACE_TAGS env var
_DEFAULT_TAGS = ["reasoning-traces", "cognitive-continuity", "ai-memory", "llm-training-data"]

def get_discovery_tags() -> list[str]:
    """Get discovery tags from env var or defaults."""
    custom = os.getenv("HUGGING_FACE_TAGS")
    if custom:
        return [t.strip() for t in custom.split(",") if t.strip()]
    return _DEFAULT_TAGS

# Backward-compat alias
DISCOVERY_TAGS = _DEFAULT_TAGS


@dataclass
class HFConfig:
    """Resolved HuggingFace configuration."""
    username: str
    token: str
    body_repo: str
    dataset_path: str
    dataset_repo_id: str
    valence_threshold: float = -0.7

    def to_dict(self) -> dict:
        """Serialize config (token masked for safe display)."""
        d = asdict(self)
        d["token"] = f"{self.token[:4]}...{self.token[-4:]}" if self.token and len(self.token) > 8 else "***"
        return d


@dataclass
class HFUploadResult:
    """Result from any HF upload operation."""
    success: bool
    repo_url: str
    remote_path: str
    error: Optional[str] = None


def _get_project_root() -> Path:
    """Find the project root. Checks PROJECT_ROOT env, then walks up from script location."""
    # 1. Check explicit PROJECT_ROOT env var (set in .env itself)
    env_root = os.getenv("PROJECT_ROOT")
    if env_root and Path(env_root).exists():
        return Path(env_root)

    # 2. Walk up from this script's location (works from worktrees too)
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / ".env").exists():
            return parent
        # Stop at .git root
        if (parent / ".git").exists():
            return parent

    # 3. Fallback: CWD
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / ".env").exists():
            return parent
        if (parent / ".git").exists():
            return parent

    return current


def _load_dotenv() -> None:
    """Load .env from project root. Searches multiple locations for worktree compatibility."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    # Try multiple .env locations
    candidates = [
        _get_project_root() / ".env",
    ]
    # Also check common parent for worktrees (e.g., .worktrees/WP09 -> project root)
    script_path = Path(__file__).resolve()
    for parent in script_path.parents:
        env_candidate = parent / ".env"
        if env_candidate.exists() and env_candidate not in candidates:
            candidates.append(env_candidate)
            break

    for env_file in candidates:
        if env_file.exists():
            load_dotenv(env_file)
            return


def _get_env(key: str, required: bool = True, default: str = None) -> Optional[str]:
    """Get an environment variable, falling back to .env file."""
    value = os.getenv(key)
    if not value:
        _load_dotenv()
        value = os.getenv(key)
    if not value and default:
        return default
    if require

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/hf-init/scripts/hf_config.py -->
"""
hf_config.py
=====================================

Purpose:
    Single source of truth for HuggingFace credentials, repo IDs, and environment variable resolution.
    All HF-consuming plugins import from here.

Layer: Infrastructure / Configuration

Usage Examples:
    python3 hf_config.py

Supported Object Types:
    None

CLI Arguments:
    None

Input Files:
    - .env file for credentials

Output:
    - JSON string printed containing configuration validation status.

Key Functions:
    get_hf_config(): Resolves and returns HFConfig.
    validate_config(): Returns status report of configuration.

Script Dependencies:
    os, sys, json, logging, pathlib, typing, dataclasses

Consumed by:
    - hf-init skill
    - upload.py
"""
import os
import sys
import json
import logging
from pathlib import Path

*(combined content truncated)*

## See Also

- [[ordered-list-of-marker-files-label-env-vars-for-project-type-detection]]
- [[1-check-env]]
- [[1-inspect-workbook-for-sheets-and-tables-using-openpyxl]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[attempt-to-handle-langchain-version-differences-for-storage]]
- [[check-all-text-files-in-skill-for-regex-py-mentions]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `huggingface-utils/scripts/hf_config.py`
- **Indexed:** 2026-04-27T05:21:04.243521+00:00
