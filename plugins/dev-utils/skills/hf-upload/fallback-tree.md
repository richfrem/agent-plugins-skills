# Procedural Fallback Tree: hf-upload

## 1. hf-init Not Run (Credentials Not Configured)
If `hf_config.py` validation fails before an upload:
- **Action**: HALT. Do NOT attempt any upload. Report that hf-init must be run first. Provide the init command.

## 2. Rate Limit (429) After 5 Backoff Retries
If all 5 exponential backoff retry attempts are exhausted:
- **Action**: Report the final failure with the upload target and error details. Do NOT silently drop the upload. Ask the user to retry manually later or check HF API status.

## 3. HFUploadResult.success is False
If any upload operation returns `success=False`:
- **Action**: Report the `error` field from the result. Do NOT proceed to downstream operations that depend on this upload. Ask user whether to retry or abort.

## 4. Valence Filter Rejection
If `upload_soul_snapshot()` is called with valence below `SOUL_VALENCE_THRESHOLD`:
- **Action**: Report the exact valence score and the configured threshold. Do NOT upload. Ask the user to review the content or override the threshold explicitly.
