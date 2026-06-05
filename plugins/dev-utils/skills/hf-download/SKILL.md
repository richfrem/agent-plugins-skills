---
name: hf-download
plugin: huggingface-utils
description: "Download primitives for HuggingFace assets - files, folder snapshots, and model weights with exponential backoff on rate limits. Use when pulling models, datasets, or caches from HuggingFace to the local environment."
allowed-tools: Bash, Read
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# HuggingFace Download Primitives

**Status:** Active
**Author:** Richard Fremmerlid
**Domain:** HuggingFace Integration
**Depends on:** `hf-init` (credentials must be configured first)

## Purpose

Provides consolidated download operations for all HF-consuming plugins (Primary Agent, local-llm-bench, etc.) to fetch files, models, and snapshots. All downloads include exponential backoff for rate-limit handling.

## Available Operations

| Function | Description | Source Repo |
|---|---|---|
| `download_file()` | Download a single file | Custom or default repo |
| `download_folder()` | Download an entire folder snapshot | Custom or default repo |

## Usage

### From Python (as a library)
```python
from hf_download import download_file, download_folder
from pathlib import Path

# Download a single file from dataset repository to local directory
local_file_path = await download_file(
    filename="data/soul_traces.jsonl",
    local_dir=Path("./local_data")
)

# Download a model snapshot (e.g. GGUF weights)
model_dir = await download_folder(
    local_dir=Path("./models"),
    repo_id="unsloth/gemma-4-12b-it-GGUF",
    repo_type="model",
    allow_patterns=["*UD-Q4_K_XL.gguf"]
)
```

### From CLI
```bash
# Download a single file
python ./hf_download.py --filename data/soul_traces.jsonl --local-dir ./local_data

# Download a specific model snapshot using glob patterns
python ./hf_download.py \
  --repo-id unsloth/gemma-4-12b-it-GGUF \
  --repo-type model \
  --allow-patterns "*UD-Q4_K_XL.gguf" \
  --local-dir ./models
```

### Prerequisites
1. Run `hf-init` first to validate credentials and dataset structure.
2. Requires `huggingface_hub` installed (`pip install huggingface_hub`).
3. Environment variables: `HUGGING_FACE_USERNAME`, `HUGGING_FACE_TOKEN`.

## Error Handling

All operations return paths on success or raise appropriate exceptions with exponential backoff retries (up to 5 attempts) on rate limits or API connectivity issues.
