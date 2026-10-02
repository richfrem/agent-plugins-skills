---
name: hf-init
plugin: dev-utils
description: Initialize HuggingFace integration - validates environment variables, tests API connectivity, and sets up dataset repository structure.
allowed-tools: Bash, Read
---

# HuggingFace Initialization (`hf-init`)

Sets up credentials, connectivity, and dataset repository structure for HuggingFace persistence.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Required Environment Variables](#required-environment-variables)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

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

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria and security validation for HuggingFace initialization.
- [fallback-tree.md](references/fallback-tree.md) — Fallback protocol when credentials or variables are missing.
