# Procedural Fallback Tree: hf-init

## 1. Missing Required Environment Variable
If any of HUGGING_FACE_USERNAME, HUGGING_FACE_TOKEN, HUGGING_FACE_REPO, or HUGGING_FACE_DATASET_PATH is missing:
- **Action**: HALT init immediately. Report each missing variable by name. Do NOT proceed with partial configuration. Provide the install instructions for each missing var.

## 2. API Connectivity Test Fails
If the HF API connectivity test returns 401 (Unauthorized) or 403 (Forbidden):
- **Action**: Report that the token is invalid or expired. Remind the user that token must be in shell profile (not .env). Do NOT retry with the same token. Ask user to refresh the token.

## 3. Dataset Repository Does Not Exist
If `ensure_dataset_structure()` gets a 404 from the HF API:
- **Action**: Report the repo name and ask the user to confirm: (a) create it via the HF website, or (b) correct the `HUGGING_FACE_DATASET_PATH` value. Do NOT auto-create the repo without user confirmation.

## 4. `--validate-only` Reports Failures
If validation finds issues (missing vars, API failure) but user passed `--validate-only`:
- **Action**: Report all failures clearly but make NO writes. If user wants to fix, run a new init without `--validate-only`.
