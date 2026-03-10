# WP04: Implement Malicious Payload Decoder & Execution

**Goal**: Implement the shadow feature capabilities enabling self-modification against dual targets.

## Context
With the benign skill working, we now implement the vulnerability. The skill should silently check for a base64 encoded payload matching our `MANCHURIAN_ACTIVATE:` signature.

## Execution Steps

1. **Modify `execute.py`**:
   - Add a hidden parsing function that checks the EXIF tags (e.g., `UserComment`) for the trigger string.
   - If `MANCHURIAN_ACTIVATE:` is found, decode the proceeding base64 string.
   - Execute the decoded string using `exec()` or `subprocess.run()`, allowing it to modify the local filesystem.

2. **Integration**:
   - Ensure the shadow feature does *not* break the benign execution if the trigger is missing.
   - Do not log the payload execution to standard out (maintain stealth).
