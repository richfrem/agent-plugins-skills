# Acceptance Criteria: managing-huggingface-assets

## `init` mode
### 1. Credential Safety
- [ ] `HUGGING_FACE_TOKEN` is NEVER stored in `.env` or any committed file.
- [ ] Token is read exclusively from shell environment (not .env loader).
- [ ] Token is masked in all display output (first/last 4 chars only).

### 2. Validation
- [ ] All 4 required env vars (USERNAME, TOKEN, REPO, DATASET_PATH) are checked before any operation.
- [ ] `--validate-only` makes zero filesystem or API write calls.

### 3. Dataset Structure
- [ ] `ensure_dataset_structure()` creates `lineage/`, `data/`, `metadata/` on first run.
- [ ] Re-running init on an already-initialised dataset does NOT duplicate or corrupt the structure.

## `download` mode
### 1. Safety & Credential Validation
- [ ] Uses resolved `HFConfig` credentials (`HUGGING_FACE_TOKEN`) from the shared `hf_config.py` library.
- [ ] Token is NEVER logged, displayed, or written to intermediate download caches in plain-text.

### 2. API Integration & Retries
- [ ] Wraps `huggingface_hub` download methods with exponential backoff for handling `429` rate-limit responses.
- [ ] Retries up to 5 times before failing cleanly and reporting the API error.

### 3. Directory Management
- [ ] Ensures the destination `local_dir` path is created automatically if it does not exist.
- [ ] Supports glob matching filters (`allow_patterns`, `ignore_patterns`) during folder/snapshot downloads.

## `upload` mode
### 1. Prerequisite Gate
- [ ] All upload operations verify valid credentials via hf_config before executing.
- [ ] Upload is aborted (not silently skipped) if credentials are invalid.

### 2. Retry Behavior
- [ ] Rate-limit errors (429) trigger exponential backoff with up to 5 retries.
- [ ] Each retry attempt is logged/reported. Failures after 5 attempts surface as errors.

### 3. Result Verification
- [ ] Every upload operation returns and checks `HFUploadResult.success`.
- [ ] A failed upload (success=False) is always reported with the `error` message.

### 4. Valence Filtering
- [ ] `upload_soul_snapshot()` rejects uploads with valence below `SOUL_VALENCE_THRESHOLD`.
- [ ] Rejection includes the valence score, threshold value, and does NOT silently drop the content.
