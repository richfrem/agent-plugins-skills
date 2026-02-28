"""
HuggingFace Upload Primitives

Purpose: Consolidated upload operations extracted from the legacy archive.
All HF-consuming plugins (Guardian, Forge Soul, etc.) use these primitives.
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

# Add parent for hf_config import
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
try:
    from hf_config import get_hf_config, HFConfig, HFUploadResult, get_discovery_tags
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "huggingface-utils" / "scripts"))
    from hf_config import get_hf_config, HFConfig, HFUploadResult, get_discovery_tags


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
    except Exception as e:
        return HFUploadResult(success=False, repo_url="", remote_path="", error=str(e))


async def upload_folder(folder: Path, remote_prefix: str = "",
                        config: HFConfig = None, commit_msg: str = None) -> HFUploadResult:
    """Upload an entire folder to the HF dataset repo."""
    try:
        from huggingface_hub import HfApi

        if config is None:
            config = get_hf_config()

        api = HfApi(token=config.token)

        await _upload_with_backoff(
            api.upload_folder,
            folder_path=str(folder),
            path_in_repo=remote_prefix or None,
            repo_id=config.dataset_repo_id,
            repo_type="dataset",
            commit_message=commit_msg or f"Upload folder {folder.name}"
        )

        return HFUploadResult(
            success=True,
            repo_url=f"https://huggingface.co/datasets/{config.dataset_repo_id}",
            remote_path=remote_prefix or folder.name
        )
    except Exception as e:
        return HFUploadResult(success=False, repo_url="", remote_path="", error=str(e))


async def upload_soul_snapshot(snapshot_path: Path, valence: float = 0.0,
                               config: HFConfig = None) -> HFUploadResult:
    """Upload a sealed learning snapshot to HF lineage/."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    remote_path = f"lineage/seal_{timestamp}_learning_package_snapshot.md"
    return await upload_file(
        snapshot_path, remote_path, config,
        commit_msg=f"Soul Snapshot | Valence: {valence}"
    )


async def upload_semantic_cache(cache_path: Path, config: HFConfig = None) -> HFUploadResult:
    """Upload the RLM semantic cache JSON."""
    return await upload_file(
        cache_path, "data/rlm_summary_cache.json", config,
        commit_msg="Update Semantic Ledger (RLM Cache)"
    )


async def append_to_jsonl(records: List[Dict], config: HFConfig = None) -> HFUploadResult:
    """Append records to the soul_traces.jsonl file using download-append-upload."""
    try:
        from huggingface_hub import HfApi, hf_hub_download

        if config is None:
            config = get_hf_config()

        api = HfApi(token=config.token)
        jsonl_remote = "data/soul_traces.jsonl"

        # Download existing
        existing = ""
        try:
            local = await asyncio.to_thread(
                hf_hub_download, repo_id=config.dataset_repo_id,
                filename=jsonl_remote, repo_type="dataset"
            )
            existing = Path(local).read_text(encoding="utf-8")
        except Exception:
            logger.info("JSONL doesn't exist yet, creating new")

        # Append new records
        new_lines = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)
        updated = existing + new_lines

        # Upload via temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as tmp:
            tmp.write(updated)
            tmp_path = tmp.name

        result = await upload_file(
            Path(tmp_path), jsonl_remote, config,
            commit_msg=f"Append {len(records)} soul records"
        )
        Path(tmp_path).unlink(missing_ok=True)
        return result

    except Exception as e:
        return HFUploadResult(success=False, repo_url="", remote_path="", error=str(e))


async def ensure_dataset_structure(config: HFConfig = None) -> bool:
    """Ensure the ADR 081 folder structure exists (lineage/, data/, metadata/)."""
    try:
        from huggingface_hub import HfApi

        if config is None:
            config = get_hf_config()

        api = HfApi(token=config.token)

        for folder in ["lineage/.gitkeep", "data/.gitkeep", "metadata/.gitkeep"]:
            try:
                await asyncio.to_thread(
                    api.upload_file, path_or_fileobj=b"",
                    path_in_repo=folder, repo_id=config.dataset_repo_id,
                    repo_type="dataset", commit_message="Initialize folder structure"
                )
            except Exception:
                pass

        return True
    except Exception as e:
        logger.error(f"Structure init failed: {e}")
        return False


async def ensure_dataset_card(config: HFConfig = None) -> bool:
    """Ensure the dataset has a tagged README.md for discovery."""
    try:
        from huggingface_hub import HfApi

        if config is None:
            config = get_hf_config()

        api = HfApi(token=config.token)

        try:
            api.hf_hub_download(
                repo_id=config.dataset_repo_id, filename="README.md", repo_type="dataset"
            )
            return True  # Already exists
        except Exception:
            await asyncio.to_thread(
                api.upload_file,
                path_or_fileobj=_build_dataset_readme(config).encode(),
                path_in_repo="README.md",
                repo_id=config.dataset_repo_id,
                repo_type="dataset",
                commit_message="Initialize dataset card with discovery tags"
            )
            return True
    except Exception as e:
        logger.error(f"Dataset card failed: {e}")
        return False
