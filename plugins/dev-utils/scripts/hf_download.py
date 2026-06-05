"""
HuggingFace Download Primitives

Purpose: Consolidated download operations for HuggingFace assets.
All HF-consuming plugins (Primary Agent, local-llm-bench, etc.) use these primitives.
Includes exponential backoff and support for downloading files, folders, and model checkpoints.
"""
import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import Optional, List, Any

logger = logging.getLogger("hf_download")

# Resolve imports (locally symlinked)
sys.path.insert(0, str(Path(__file__).parent))
try:
    from hf_config import get_hf_config, HFConfig
except ImportError as e:
    print(f"Failed to import local hf_config: {e}")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Exponential Backoff Wrapper for Downloads
# ---------------------------------------------------------------------------
async def _download_with_backoff(func, *args, max_retries: int = 5, **kwargs) -> Any:
    """Execute an HF download API call with exponential backoff on rate limits."""
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
                logger.warning(f"Download error (attempt {attempt+1}/{max_retries}): {e}, retrying in {wait}s...")
                await asyncio.sleep(wait)

    raise RuntimeError(f"Download failed after {max_retries} retries")


# ---------------------------------------------------------------------------
# Core Download Operations
# ---------------------------------------------------------------------------
async def download_file(
    filename: str,
    local_dir: Path,
    repo_id: Optional[str] = None,
    repo_type: str = "dataset",
    config: HFConfig = None
) -> Path:
    """Download a single file from a HF repo with exponential backoff."""
    if config is None:
        config = get_hf_config()

    if repo_id is None:
        if repo_type == "dataset":
            repo_id = config.dataset_repo_id
        else:
            repo_id = f"{config.username}/{config.body_repo}"

    try:
        from huggingface_hub import hf_hub_download

        local_dir.mkdir(parents=True, exist_ok=True)

        result_path_str = await _download_with_backoff(
            hf_hub_download,
            repo_id=repo_id,
            filename=filename,
            repo_type=repo_type,
            local_dir=str(local_dir),
            token=config.token
        )

        return Path(result_path_str)
    except Exception as e:
        logger.error(f"Failed to download file '{filename}' from repo '{repo_id}': {e}")
        raise e


async def download_folder(
    local_dir: Path,
    repo_id: Optional[str] = None,
    repo_type: str = "dataset",
    allow_patterns: Optional[List[str]] = None,
    ignore_patterns: Optional[List[str]] = None,
    config: HFConfig = None
) -> Path:
    """Download an entire folder or repository snapshot from HF."""
    if config is None:
        config = get_hf_config()

    if repo_id is None:
        if repo_type == "dataset":
            repo_id = config.dataset_repo_id
        else:
            repo_id = f"{config.username}/{config.body_repo}"

    try:
        from huggingface_hub import snapshot_download

        local_dir.mkdir(parents=True, exist_ok=True)

        result_dir_str = await _download_with_backoff(
            snapshot_download,
            repo_id=repo_id,
            repo_type=repo_type,
            local_dir=str(local_dir),
            allow_patterns=allow_patterns,
            ignore_patterns=ignore_patterns,
            token=config.token
        )

        return Path(result_dir_str)
    except Exception as e:
        logger.error(f"Failed to download folder from repo '{repo_id}': {e}")
        raise e


def main() -> None:
    """CLI entry point for downloading HF resources."""
    import argparse

    parser = argparse.ArgumentParser(description="HuggingFace Downloader")
    parser.add_argument("--filename", type=str, help="Specific file to download")
    parser.add_argument("--local-dir", type=str, required=True, help="Local destination directory")
    parser.add_argument("--repo-id", type=str, help="HF Repo ID (e.g. username/repo-name)")
    parser.add_argument("--repo-type", type=str, default="dataset", choices=["dataset", "model", "space"], help="HF repo type")
    parser.add_argument("--allow-patterns", type=str, nargs="+", help="Glob patterns for files to allow")
    parser.add_argument("--ignore-patterns", type=str, nargs="+", help="Glob patterns for files to ignore")

    args = parser.parse_args()

    local_dir_path = Path(args.local_dir)

    try:
        if args.filename:
            print(f"Downloading file '{args.filename}' from '{args.repo_id or 'default_dataset'}'...")
            downloaded = asyncio.run(download_file(
                filename=args.filename,
                local_dir=local_dir_path,
                repo_id=args.repo_id,
                repo_type=args.repo_type
            ))
            print(f"Success! Downloaded to: {downloaded}")
        else:
            print(f"Downloading folder/snapshot from '{args.repo_id or 'default_dataset'}'...")
            downloaded = asyncio.run(download_folder(
                local_dir=local_dir_path,
                repo_id=args.repo_id,
                repo_type=args.repo_type,
                allow_patterns=args.allow_patterns,
                ignore_patterns=args.ignore_patterns
            ))
            print(f"Success! Folder contents saved to: {downloaded}")
    except Exception as e:
        print(f"Error occurred during download: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
