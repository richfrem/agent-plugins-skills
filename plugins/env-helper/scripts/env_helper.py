"""
# Purpose: Shared ecosystem environment variable helper for Project Sanctuary plugins.
# Provides safe resolution of HuggingFace credentials, project root, and dataset config
# without any dependency on internal shared libraries.
#
# Usage:
#   python3 plugins/env-helper/scripts/env_helper.py --key HF_TOKEN
#   python3 plugins/env-helper/scripts/env_helper.py --key HF_DATASET_REPO
#   python3 plugins/env-helper/scripts/env_helper.py --all
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Env file discovery
# ---------------------------------------------------------------------------

def _find_env_file(start: Path) -> Optional[Path]:
    """Walk up the directory tree looking for a .env file."""
    current = start.resolve()
    for parent in [current, *current.parents]:
        candidate = parent / ".env"
        if candidate.exists():
            return candidate
    return None


def _load_dotenv(env_file: Path) -> None:
    """Minimal .env loader that sets os.environ without relying on python-dotenv."""
    try:
        with open(env_file, "r", encoding="utf-8") as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Core resolution helpers
# ---------------------------------------------------------------------------

def _get_project_root() -> Path:
    """Return the project root: the git root, or the directory containing this script's plugin."""
    here = Path(__file__).resolve()
    # Walk up to find .git
    for parent in [here, *here.parents]:
        if (parent / ".git").exists():
            return parent
    # Fallback: go up three levels (scripts/ -> plugin/ -> plugins/ -> root)
    return here.parents[3]


DEFAULTS: dict[str, str] = {
    "HF_DATASET_REPO": "SanctuaryDB",
    "HF_LINEAGE_FOLDER": "lineage",
    "HF_SOUL_TRACES_FILE": "data/soul_traces.jsonl",
}

REQUIRED: list[str] = [
    "HF_TOKEN",
    "HF_USERNAME",
]


def resolve(key: str) -> Optional[str]:
    """Return the value of *key* from environment or .env file, or None."""
    project_root = _get_project_root()
    env_file = _find_env_file(project_root)
    if env_file:
        _load_dotenv(env_file)
    value = os.environ.get(key)
    if value is None:
        value = DEFAULTS.get(key)
    return value


def resolve_all() -> dict[str, Optional[str]]:
    """Resolve all known ecosystem constants and return as a dict."""
    all_keys = set(REQUIRED) | set(DEFAULTS.keys())
    return {k: resolve(k) for k in sorted(all_keys)}


def resolve_hf_config() -> dict[str, Optional[str]]:
    """Convenience: return the HuggingFace upload configuration block."""
    username = resolve("HF_USERNAME")
    repo_name = resolve("HF_DATASET_REPO")
    return {
        "hf_token": resolve("HF_TOKEN"),
        "hf_username": username,
        "dataset_repo": f"{username}/{repo_name}" if username and repo_name else None,
        "lineage_folder": resolve("HF_LINEAGE_FOLDER"),
        "soul_traces_file": resolve("HF_SOUL_TRACES_FILE"),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resolve Project Sanctuary ecosystem environment constants."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--key", metavar="KEY", help="Resolve a single environment variable.")
    group.add_argument("--all", action="store_true", help="Resolve and print all known constants.")
    group.add_argument("--hf-config", action="store_true", help="Print the HuggingFace upload config block as JSON.")
    args = parser.parse_args()

    if args.key:
        value = resolve(args.key)
        if value is None:
            print(f"ERROR: {args.key} is not set and has no default.", file=sys.stderr)
            sys.exit(1)
        print(value)
    elif getattr(args, "all", False):
        print(json.dumps(resolve_all(), indent=2))
    elif args.hf_config:
        print(json.dumps(resolve_hf_config(), indent=2))


if __name__ == "__main__":
    main()
