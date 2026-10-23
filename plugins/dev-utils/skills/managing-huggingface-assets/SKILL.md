---
name: managing-huggingface-assets
plugin: dev-utils
description: >
  Sets up, downloads from and uploads to HuggingFace repositories with credential hygiene
  and exponential backoff. Use to validate HuggingFace credentials and dataset structure,
  download files, snapshots or model weights, or upload files, folders, learning snapshots
  and JSONL traces. Not for searching the Hub or other storage providers.
allowed-tools: Bash, Read, Write
---

# Managing HuggingFace Assets (`managing-huggingface-assets`)

Three modes share one credential library (`scripts/hf_config.py`).

## Contents

- [Constraints](#constraints) • [Quick Start](#quick-start) • [Modes](#modes) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

- **Secret hygiene**: `HUGGING_FACE_TOKEN` comes only from the shell environment; never write it to `.env`, Git, arguments or logs.
- **Backoff**: retry HTTP 429/503 with exponential backoff, up to 5 attempts, then report the failure.
- **Init first**: uploads and downloads require a passing `init` validation; halt if credentials are invalid.
- **Remote layout**: datasets use `lineage/`, `data/` and `metadata/`.

## Dependencies

Requires Python 3.8+ (standard library only).

## Quick Start

```bash
python3 scripts/hf_init.py --validate-only
python3 scripts/hf_download.py --filename data/soul_traces.jsonl --local-dir ./local_data
python3 scripts/hf_upload.py --file lineage/sealed_trace.md --remote-path lineage/sealed_trace.md
```

## Modes

| Mode | Script | Use for | Reference |
|---|---|---|---|
| `init` | `scripts/hf_init.py` | Validate env vars, test connectivity, create dataset structure | [init.md](references/init.md) |
| `download` | `scripts/hf_download.py` | Files, folder snapshots, model weights | [download.md](references/download.md) |
| `upload` | `scripts/hf_upload.py` | Files, folders, soul snapshots, JSONL appends | [upload.md](references/upload.md) |

## Workflow

1. Pick the mode from the table and read its reference.
2. Run `init --validate-only` when credentials have not been verified this session.
3. Run the mode's script; follow [fallback-tree.md](references/fallback-tree.md) on any failure.
4. Confirm the result: files present and non-empty (download), or `HFUploadResult.success` (upload).

## Verification

```bash
python3 scripts/hf_config.py
```

Check the mode's section in [acceptance-criteria.md](references/acceptance-criteria.md).

## References

- [init.md](references/init.md) • [download.md](references/download.md) • [upload.md](references/upload.md)
- [acceptance-criteria.md](references/acceptance-criteria.md) • [fallback-tree.md](references/fallback-tree.md)
