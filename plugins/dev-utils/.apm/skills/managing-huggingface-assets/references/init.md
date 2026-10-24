# HuggingFace setup and validation (`init` mode)

Sets up credentials, connectivity, and dataset repository structure for HuggingFace persistence.

## Critical Constraints

1. **Secret Hygiene**: Tokens must be stored in shell profile (`~/.zshrc`), NEVER committed to `.env` or Git.
2. **Repository Structure**: Enforces standard folder structure (`lineage/`, `data/`, `metadata/`).

## Quick start

Validate HuggingFace configuration without modifying remote repositories:

```bash
python3 scripts/hf_init.py --validate-only
```

## Required Environment Variables

| Variable | Required | Description |
|---|---|---|
| `HUGGING_FACE_USERNAME` | Yes | HuggingFace account username |
| `HUGGING_FACE_TOKEN` | Yes | Hub API token (in shell profile) |
| `HUGGING_FACE_REPO` | Yes | Model repository name |
| `HUGGING_FACE_DATASET_PATH` | Yes | Dataset repository name |
| `HUGGING_FACE_TAGS` | No | Comma-separated discovery tags |
| `HUGGING_FACE_PROJECT_NAME` | No | Display name for dataset card |

## Workflow

1. **Credential Validation**: Verify presence of required environment variables.
2. **Connectivity Test**: Run API probe to confirm read/write token privileges.
3. **Repository Setup**: Initialize standard directory structure (`lineage/`, `data/`, `metadata/`) on remote dataset.
4. **Readiness Report**: Output connection status and configured paths.

## Verification

Confirm configuration and authentication validity:

```bash
python3 scripts/hf_config.py
```
