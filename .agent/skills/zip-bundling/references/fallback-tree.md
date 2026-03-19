# Procedural Fallback Tree: ZIP Bundling

## 1. bundle_zip.py Command Fails
If invoking the Python script throws an error (e.g., missing dependency, path error):
- **Action**: Review the script output. If the JSON manifest is malformed, fix it and retry. If a system dependency is missing, report it to the user. Do NOT attempt to run raw `zip` shell commands instead of the script.

## 2. Missing File During Archiving
If `bundle_zip.py` reports that it skipped a file because it wasn't found:
- **Action**: This is normal behavior for the script (it injects a note in `_manifest_notes.md`). Merely report the exclusion to the user when confirming the ZIP is ready. Do NOT treat it as a fatal script failure.

## 3. Directory Contains Massive Unintended Binaries
If passing a directory like `public/` causes the script to zip large media files not meant for LLMs:
- **Action**: Do not abort midway, but when presenting the ZIP, warn the user about the size. Ask if they want to regenerate the manifest excluding specific extensions (e.g., `*.mp4`).

## 4. Manifest JSON Validation Failure
If the script rejects `file-manifest.json` due to missing `path` or `note` keys:
- **Action**: Correct the JSON file on disk immediately to ensure every record has both `"path"` and `"note"`, then re-invoke the script.
