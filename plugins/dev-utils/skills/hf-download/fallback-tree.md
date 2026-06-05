# Procedural Fallback Tree: hf-download

## 1. Missing or Invalid Credentials
If the API returns `401 Unauthorized` or `403 Forbidden`:
- **Action**: Check if the token is present in the environment. Verify the token scope has read access. Suggest running `hf-init` to test config connectivity.

## 2. Resource/Repository Not Found (404)
If the requested file or repository ID is not found on HuggingFace:
- **Action**: Log the exact repo ID and file path. Halt download. Suggest verifying the repository ID spelling, checking if it is a private repository that requires login permission, or trying community/public mirrors.

## 3. Directory Permission Denied
If the local destination folder cannot be created or written to:
- **Action**: Report the filesystem write permission error. Do not attempt further API queries. Recommend running under correct user permissions or target a different directory (e.g. within user workspace).

## 4. Rate-Limit Exceeded (429)
If rate limit limits are hit:
- **Action**: Run exponential backoff loop up to 5 attempts, scaling wait time as `2^attempt` seconds. If it still fails, report connection timeout/limit issues and recommend waiting before retry.
