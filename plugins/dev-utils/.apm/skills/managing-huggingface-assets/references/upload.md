# HuggingFace upload (`upload` mode)

Persists files, folders, soul learning snapshots, and semantic caches to HuggingFace repositories with exponential backoff.

## Critical Constraints

- **Credential Hygiene**: Consume `HUGGING_FACE_TOKEN` exclusively via environment variables; never embed tokens.
- **Rate-Limit Resilience**: Requests retry with exponential backoff (up to 5 attempts) on rate limits or connectivity issues.
- **Remote Structure Standards**: Conform to ADR 081 layout conventions (`lineage/`, `data/`, `metadata/`).
- **Upload Scope**: Dedicated to uploading and persisting assets. For downloading models or datasets, use the `download` mode.

## Dependencies

Requires Python 3.8+ (standard library only).

## Quick start

```bash
# Upload a single file
python3 scripts/hf_upload.py \
  --file lineage/sealed_trace.md \
  --remote-path lineage/sealed_trace.md

# Upload an entire directory
python3 scripts/hf_upload.py \
  --folder ./data \
  --remote-path data/
```

## Workflow

1. **Phase 1: Environment & Token Check**: Validate `HUGGING_FACE_TOKEN` and dataset repository write permissions.
2. **Phase 2: Remote Target Path Definition**: Ensure remote path maps to ADR 081 structure (`lineage/`, `data/`, `metadata/`).
3. **Phase 3: Execution with Backoff**: Call `hf_upload.py` CLI or Python library (`upload_file`, `upload_soul_snapshot`, `append_to_jsonl`).
4. **Phase 4: Remote Confirmation**: Validate `HFUploadResult.success` and report destination URL.

## Verification

```bash
# Verify CLI help and script loading
python3 scripts/hf_upload.py --help

```
