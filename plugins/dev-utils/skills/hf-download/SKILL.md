---
name: hf-download
plugin: dev-utils
description: >
  Download primitives for HuggingFace assets - files, folder snapshots, and model weights with exponential backoff on rate limits. Use when pulling models, datasets, or caches from HuggingFace to the local environment.
allowed-tools: Bash, Read
---

# HuggingFace Download Primitives (`hf-download`)

Fetches files, folder snapshots, and model weights from HuggingFace repositories with built-in exponential backoff.

## Contents

- [Critical Constraints](#critical-constraints)
- [Dependencies](#dependencies)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

- **Credential Hygiene**: Consume `HUGGING_FACE_TOKEN` exclusively via environment variables; never embed tokens in arguments or logs.
- **Rate-Limit Resilience**: Operations must employ exponential backoff (up to 5 retries) on HTTP 429/503 errors.
- **Target Path Containment**: Restrict download destinations to designated working folders (`./local_data`, `./models`).
- **Download Scope**: Dedicated to fetching assets. For uploading snapshots or soul traces, use `hf-upload`.

## Dependencies

Requires Python 3.8+ (standard library only).

## Quick start

```bash
# Download a single file from repository
python3 plugins/dev-utils/skills/hf-download/scripts/hf_download.py \
  --filename data/soul_traces.jsonl \
  --local-dir ./local_data

# Download a model snapshot with pattern matching
python3 plugins/dev-utils/skills/hf-download/scripts/hf_download.py \
  --repo-id unsloth/gemma-4-12b-it-GGUF \
  --repo-type model \
  --allow-patterns "*UD-Q4_K_XL.gguf" \
  --local-dir ./models
```

## Workflow

1. **Phase 1: Environment & Token Check**: Verify `huggingface_hub` installation and presence of `HUGGING_FACE_TOKEN`.
2. **Phase 2: Target Path & Parameter Selection**: Select repository ID, asset type (`dataset` or `model`), and destination path.
3. **Phase 3: Execution with Backoff**: Run `hf_download.py` via CLI or asynchronous Python API.
4. **Phase 4: Asset Integrity Verification**: Confirm that target files or model artifacts are present and non-empty.

## Verification

```bash
# Verify CLI help and script loading
python3 plugins/dev-utils/skills/hf-download/scripts/hf_download.py --help

# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/dev-utils/skills/hf-download --mode source
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria and verification checklist.
- [fallback-tree.md](references/fallback-tree.md) — Procedural fallback handling for download failures.
