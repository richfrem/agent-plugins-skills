# Acceptance Criteria: ZIP Bundling

## 1. Manifest Enforcement
- [ ] Agent always generates a valid `./file-manifest.json` on disk BEFORE invoking the Python archiver.
- [ ] Every item in the manifest includes a substantive `"note"` to provide context.

## 2. Script Delegation
- [ ] Agent relies strictly on `python3 bundle_zip.py` to compile the archive and generate `_manifest_notes.md`.
- [ ] Agent does NOT manually invoke `zip` or `tar` shell commands to bypass the script logic.

## 3. Resilience
- [ ] Missing files are accommodated by the script and documented in the manifest notes, without crashing the execution flow.
- [ ] Agent successfully warns the user against bundling massive binary directories.
