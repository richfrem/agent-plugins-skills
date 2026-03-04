# Acceptance Criteria: hf-upload

## 1. Prerequisite Gate
- [ ] All upload operations verify valid credentials via hf_config before executing.
- [ ] Upload is aborted (not silently skipped) if credentials are invalid.

## 2. Retry Behavior
- [ ] Rate-limit errors (429) trigger exponential backoff with up to 5 retries.
- [ ] Each retry attempt is logged/reported. Failures after 5 attempts surface as errors.

## 3. Result Verification
- [ ] Every upload operation returns and checks `HFUploadResult.success`.
- [ ] A failed upload (success=False) is always reported with the `error` message.

## 4. Valence Filtering
- [ ] `upload_soul_snapshot()` rejects uploads with valence below `SOUL_VALENCE_THRESHOLD`.
- [ ] Rejection includes the valence score, threshold value, and does NOT silently drop the content.
