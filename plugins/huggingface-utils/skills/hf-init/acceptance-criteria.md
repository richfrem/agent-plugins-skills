# Acceptance Criteria: hf-init

## 1. Credential Safety
- [ ] `HUGGING_FACE_TOKEN` is NEVER stored in `.env` or any committed file.
- [ ] Token is read exclusively from shell environment (not .env loader).
- [ ] Token is masked in all display output (first/last 4 chars only).

## 2. Validation
- [ ] All 4 required env vars (USERNAME, TOKEN, REPO, DATASET_PATH) are checked before any operation.
- [ ] `--validate-only` makes zero filesystem or API write calls.

## 3. Dataset Structure
- [ ] `ensure_dataset_structure()` creates `lineage/`, `data/`, `metadata/` on first run.
- [ ] Re-running init on an already-initialised dataset does NOT duplicate or corrupt the structure.
