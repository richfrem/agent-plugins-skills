# Acceptance Criteria: hf-download

## 1. Safety & Credential Validation
- [ ] Uses resolved `HFConfig` credentials (`HUGGING_FACE_TOKEN`) from the shared `hf_config.py` library.
- [ ] Token is NEVER logged, displayed, or written to intermediate download caches in plain-text.

## 2. API Integration & Retries
- [ ] Wraps `huggingface_hub` download methods with exponential backoff for handling `429` rate-limit responses.
- [ ] Retries up to 5 times before failing cleanly and reporting the API error.

## 3. Directory Management
- [ ] Ensures the destination `local_dir` path is created automatically if it does not exist.
- [ ] Supports glob matching filters (`allow_patterns`, `ignore_patterns`) during folder/snapshot downloads.
