# Procedural Fallback Tree: managing-huggingface-assets

## `init` mode
### 1. Missing Required Environment Variable
If any of HUGGING_FACE_USERNAME, HUGGING_FACE_TOKEN, HUGGING_FACE_REPO, or HUGGING_FACE_DATASET_PATH is missing:
- **Action**: HALT init immediately. Report each missing variable by name. Do NOT proceed with partial configuration. Provide the install instructions for each missing var.

### 2. API Connectivity Test Fails
If the HF API connectivity test returns 401 (Unauthorized) or 403 (Forbidden):
- **Action**: Report that the token is invalid or expired. Remind the user that token must be in shell profile (not .env). Do NOT retry with the same token. Ask user to refresh the token.

### 3. Dataset Repository Does Not Exist
If `ensure_dataset_structure()` gets a 404 from the HF API:
- **Action**: Report the repo name and ask the user to confirm: (a) create it via the HF website, or (b) correct the `HUGGING_FACE_DATASET_PATH` value. Do NOT auto-create the repo without user confirmation.

### 4. `--validate-only` Reports Failures
If validation finds issues (missing vars, API failure) but user passed `--validate-only`:
- **Action**: Report all failures clearly but make NO writes. If user wants to fix, run a new init without `--validate-only`.

## `download` mode
### 1. Missing or Invalid Credentials
If the API returns `401 Unauthorized` or `403 Forbidden`:
- **Action**: Check if the token is present in the environment. Verify the token scope has read access. Suggest running the `init` mode to test config connectivity.

### 2. Resource/Repository Not Found (404)
If the requested file or repository ID is not found on HuggingFace:
- **Action**: Log the exact repo ID and file path. Halt download. Suggest verifying the repository ID spelling, checking if it is a private repository that requires login permission, or trying community/public mirrors.

### 3. Directory Permission Denied
If the local destination folder cannot be created or written to:
- **Action**: Report the filesystem write permission error. Do not attempt further API queries. Recommend running under correct user permissions or target a different directory (e.g. within user workspace).

### 4. Rate-Limit Exceeded (429)
If rate limit limits are hit:
- **Action**: Run exponential backoff loop up to 5 attempts, scaling wait time as `2^attempt` seconds. If it still fails, report connection timeout/limit issues and recommend waiting before retry.

## `upload` mode
### 1. init Mode Not Run (Credentials Not Configured)
If `hf_config.py` validation fails before an upload:
- **Action**: HALT. Do NOT attempt any upload. Report that the `init` mode must be run first. Provide the init command.

### 2. Rate Limit (429) After 5 Backoff Retries
If all 5 exponential backoff retry attempts are exhausted:
- **Action**: Report the final failure with the upload target and error details. Do NOT silently drop the upload. Ask the user to retry manually later or check HF API status.

### 3. HFUploadResult.success is False
If any upload operation returns `success=False`:
- **Action**: Report the `error` field from the result. Do NOT proceed to downstream operations that depend on this upload. Ask user whether to retry or abort.

### 4. Valence Filter Rejection
If `upload_soul_snapshot()` is called with valence below `SOUL_VALENCE_THRESHOLD`:
- **Action**: Report the exact valence score and the configured threshold. Do NOT upload. Ask the user to review the content or override the threshold explicitly.
