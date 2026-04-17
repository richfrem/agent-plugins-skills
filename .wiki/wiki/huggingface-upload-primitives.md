---
concept: huggingface-upload-primitives
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/huggingface-utils_hf-upload.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.321392+00:00
cluster: plugin-code
content_hash: 1d9b5b69357042f1
---

# HuggingFace Upload Primitives

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: hf-upload
description: "Upload primitives for HuggingFace Soul persistence - file, folder, snapshot, JSONL append, and dataset card management with exponential backoff. Use when persisting agent learnings, snapshots, or semantic caches to HuggingFace."
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
# HuggingFace Upload Primitives

**Status:** Active
**Author:** Richard Fremmerlid
**Domain:** HuggingFace Integration
**Depends on:** `hf-init` (credentials must be configured first)

## Purpose

Provides consolidated upload operations for all HF-consuming plugins (Primary Agent, Orchestrator, etc.). All uploads include exponential backoff for rate-limit handling.

## Available Operations

| Function | Description | Remote Path |
|---|---|---|
| `upload_file()` | Upload a single file | Custom path |
| `upload_folder()` | Upload an entire directory | Custom prefix |
| `upload_soul_snapshot()` | Upload a sealed learning snapshot | `lineage/seal_<timestamp>_*.md` |
| `upload_semantic_cache()` | Upload RLM semantic cache | `data/rlm_summary_cache.json` |
| `append_to_jsonl()` | Append records to soul traces | `data/soul_traces.jsonl` |
| `ensure_dataset_structure()` | Create ADR 081 folders | `lineage/`, `data/`, `metadata/` |
| `ensure_dataset_card()` | Create/verify tagged README.md | `README.md` |

## Usage

### From Python (as a library)
```python
from hf_upload import upload_file, upload_soul_snapshot, append_to_jsonl

# Upload a single file
result = await upload_file(Path("my_file.md"), "lineage/my_file.md")

# Upload a sealed learning snapshot
result = await upload_soul_snapshot(Path("snapshot.md"), valence=-0.5)

# Append records to soul_traces.jsonl
result = await append_to_jsonl([{"type": "learning", "content": "..."}])
```

### Prerequisites
1. Run `hf-init` first to validate credentials and dataset structure
2. Requires `huggingface_hub` installed (`pip install huggingface_hub`)
3. Environment variables: `HUGGING_FACE_USERNAME`, `HUGGING_FACE_TOKEN`

## Error Handling

All operations return `HFUploadResult` with:
- `success: bool` — whether the upload succeeded
- `repo_url: str` — HuggingFace dataset URL
- `remote_path: str` — path within the dataset
- `error: str` — error message if failed

Rate-limited requests retry with exponential backoff (up to 5 attempts).


## See Also

- [[huggingface-utils-plugin]]
- [[huggingface-init-onboarding]]
- [[acceptance-criteria-hf-upload]]
- [[procedural-fallback-tree-hf-upload]]
- [[huggingface-init-onboarding]]
- [[acceptance-criteria-hf-upload]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/huggingface-utils_hf-upload.md`
- **Indexed:** 2026-04-17T06:42:10.321392+00:00
