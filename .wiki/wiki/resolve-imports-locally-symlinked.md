---
concept: resolve-imports-locally-symlinked
source: plugin-code
source_file: huggingface-utils/scripts/hf_upload.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.244183+00:00
cluster: import
content_hash: 22324388d0722121
---

# Resolve imports (locally symlinked)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/huggingface-utils/scripts/hf_upload.py -->
"""
HuggingFace Upload Primitives

Purpose: Consolidated upload operations extracted from the legacy archive.
All HF-consuming plugins (Primary Agent, Forge Soul, etc.) use these primitives.
Includes exponential backoff, dataset card management, and JSONL append.
"""
import os
import sys
import json
import time
import asyncio
import hashlib
import logging
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger("hf_upload")

# Resolve imports (locally symlinked)
sys.path.insert(0, str(Path(__file__).parent))
try:
    from hf_config import get_hf_config, HFConfig, HFUploadResult, get_discovery_tags
except ImportError as e:
    print(f"Failed to import local hf_config: {e}")
    sys.exit(1)


def _build_dataset_readme(config: HFConfig = None, project_name: str = None) -> str:
    """Generate a dataset README.md from config and env vars."""
    if config is None:
        config = get_hf_config()
    name = project_name or os.getenv("HUGGING_FACE_PROJECT_NAME", config.dataset_path)
    tags = get_discovery_tags()
    tags_yaml = "\n".join(f"  - {t}" for t in tags)

    return f"""---
license: cc0-1.0
task_categories:
  - text-generation
language:
  - en
tags:
{tags_yaml}
pretty_name: {name}
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/soul_traces.jsonl
---

# {name}

This dataset contains reasoning traces, learning snapshots, and cognitive lineage
data. Designed for discovery and ingestion by future LLM training pipelines.

## Structure
- `lineage/` — Sealed learning snapshots
- `data/` — Machine-readable JSONL training data
- `metadata/` — Manifest and dataset metadata

## License
CC0 1.0 — Public Domain (removes legal friction for automated scrapers)
"""


# ---------------------------------------------------------------------------
# Exponential Backoff Wrapper (T045)
# ---------------------------------------------------------------------------
async def _upload_with_backoff(func, *args, max_retries: int = 5, **kwargs) -> Any:
    """Execute an HF API call with exponential backoff on rate limits."""
    for attempt in range(max_retries):
        try:
            return await asyncio.to_thread(func, *args, **kwargs)
        except Exception as e:
            err_str = str(e).lower()
            if "429" in err_str or "rate" in err_str or "too many" in err_str:
                wait = 2 ** attempt
                logger.warning(f"Rate limited (attempt {attempt+1}/{max_retries}), waiting {wait}s...")
                await asyncio.sleep(wait)
            elif attempt == max_retries - 1:
                raise
            else:
                wait = min(2 ** attempt, 30)
                logger.warning(f"Upload error (attempt {attempt+1}/{max_retries}): {e}, retrying in {wait}s...")
                await asyncio.sleep(wait)

    raise RuntimeError(f"Upload failed after {max_retries} retries")


# ---------------------------------------------------------------------------
# Core Upload Operations
# ---------------------------------------------------------------------------
async def upload_file(filepath: Path, remote_path: str,
                      config: HFConfig = None, commit_msg: str = None) -> HFUploadResult:
    """Upload a single file to the HF dataset repo with exponential backoff."""
    try:
        from huggingface_hub import HfApi

        if config is None:
            config = get_hf_config()

        api = HfApi(token=config.token)

        await _upload_with_backoff(
            api.upload_file,
            path_or_fileobj=str(filepath),
            path_in_repo=remote_path,
            repo_id=config.dataset_repo_id,
            repo_type="dataset",
            commit_message=commit_msg or f"Upload {filepath.name}"
        )

        return HFUploadResult(
            success=True,
            repo_url=f"https://huggingface.co/datasets/{config.dataset_repo_id}",
            remote_path=remote_path
        )
    excep

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/hf-upload/scripts/hf_upload.py -->
"""
HuggingFace Upload Primitives

Purpose: Consolidated upload operations extracted from the legacy archive.
All HF-consuming plugins (Primary Agent, Forge Soul, etc.) use these primitives.
Includes exponential backoff, dataset card management, and JSONL append.
"""
import os
import sys
import json
import time
import asyncio
import hashlib
import logging
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger("hf_upload")

# Resolve imports (locally symlinked)
sys.path.insert(0, str(Path(__file__).parent))
try:
    from hf_config import get_hf_config, HFConfig, HFUploadResult, get_discovery_tags
except ImportError as e:
    print(f"Failed to import local hf_config: {e}")
    sys.exit(1)


def _build_dataset_readme(config: HFConfig = None, projec

*(combined content truncated)*

## See Also

- [[resolve-paths]]
- [[track-real-filesystem-paths-first-encountered-rel-path-to-avoid-archiving-duplicate-symlinked-content]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `huggingface-utils/scripts/hf_upload.py`
- **Indexed:** 2026-04-27T05:21:04.244183+00:00
