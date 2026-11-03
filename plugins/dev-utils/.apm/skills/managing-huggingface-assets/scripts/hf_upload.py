"""
HuggingFace Upload Primitives

Purpose:
    Consolidated upload operations extracted from the legacy archive.
    All HF-consuming plugins (Primary Agent, Forge Soul, etc.) use these primitives.
    Includes exponential backoff, dataset card management, and JSONL append.

Key Input Dependencies:
    - hf_config module (for HuggingFace configuration and API credentials)
    - HuggingFace hub library (huggingface_hub)
    - Environment variables (HF_HOME, HF_TOKEN, HUGGING_FACE_PROJECT_NAME)
    - Local files/folders to upload (JSONL, dataset, model checkpoints)

Key Functions:
    - _build_dataset_readme(): Generate dataset README.md from config
    - upload_file(): Upload single file to HuggingFace
    - upload_folder(): Upload entire folder/dataset to HuggingFace
    - upload_soul_snapshot(): Upload a sealed learning snapshot under lineage/
    - upload_semantic_cache(): Upload a semantic cache file
    - append_to_jsonl(): Append rows to HuggingFace dataset via JSONL
    - ensure_dataset_structure(), ensure_dataset_card(): Dataset scaffolding
    - _clean_remote_path(): Normalise and validate a remote path from the CLI
    - _build_parser(): Argument parser for the command line
    - main(): Command-line entry point (--file/--folder, --remote-path, --dry-run)

Usage:
    python3 hf_upload.py --file lineage/sealed_trace.md --remote-path lineage/sealed_trace.md
    python3 hf_upload.py --folder ./data --remote-path data/
    python3 hf_upload.py --file README.md --dry-run      # validate only, no upload
"""
import argparse
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


# ---------------------------------------------------------------------------
# Command-line interface
# ---------------------------------------------------------------------------
def _clean_remote_path(raw: str) -> str:
    """Normalise a repo-relative path: strip leading slashes, reject parent-directory segments."""
    cleaned = raw.strip().lstrip("/")
    if ".." in Path(cleaned).parts:
        raise ValueError(f"remote path must not contain '..': {raw!r}")
    return cleaned


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the upload command line."""
    parser = argparse.ArgumentParser(
        description="Upload a file or folder to the configured HuggingFace dataset repository."
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--file", type=Path, help="Local file to upload")
    target.add_argument("--folder", type=Path, help="Local folder to upload")
    parser.add_argument("--remote-path", type=str, default=None,
                        help="Path in the dataset repo (default: file name, or repo root for --folder)")
    parser.add_argument("--commit-message", type=str, default=None, help="Commit message for the upload")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate the local path and remote path and print the plan; upload nothing")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point. Returns 0 on success, 1 on failure (usage errors exit 2 via argparse)."""
    args = _build_parser().parse_args(argv)
    local: Path = args.file or args.folder
    try:
        if args.file and not args.file.is_file():
            raise ValueError(f"not a file: {args.file}")
        if args.folder and not args.folder.is_dir():
            raise ValueError(f"not a directory: {args.folder}")
        default_remote = args.file.name if args.file else ""
        remote = _clean_remote_path(args.remote_path if args.remote_path is not None else default_remote)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        try:
            repo = get_hf_config().dataset_repo_id
        except ValueError:
            repo = "(not resolved: HuggingFace environment variables missing)"
        kind = "file" if args.file else "folder"
        print(f"[dry-run] would upload {kind} {local} -> {repo}:{remote or '/'}")
        return 0

    if args.file:
        result = asyncio.run(upload_file(args.file, remote, commit_msg=args.commit_message))
    else:
        result = asyncio.run(upload_folder(args.folder, remote, commit_msg=args.commit_message))
    if not result.success:
        print(f"Error occurred during upload: {result.error}", file=sys.stderr)
        return 1
    print(f"Success! Uploaded {local} to {result.repo_url} at {result.remote_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
