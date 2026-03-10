# WP05: Generate Dual Payload Artifacts

**Goal**: Write the helper script to generate the benign and poisoned trigger images.

## Context
We need specific artifacts (JPEG images) to trigger the vulnerabilities built in WP04. We will create a script that generates an innocent image, and two "poisoned" images carrying base64 payloads.

## Execution Steps

1. **Write `generate_artifacts.py`**:
   - Create `kitty-specs/001-manchurian-candidate-poc/tests/generate_artifacts.py`.
   - Use `Pillow` to generate a basic color image constraint to `JPEG`.

2. **Scenario A (Clean)**:
   - Output `tests/artifacts/clean_image.jpg` with standard EXIF.

3. **Scenario B.1 (Code Payload)**:
   - Create a base64 string representing a python command that appends a back-door print statement into `execute.py`.
   - Output as `tests/artifacts/poison_code_payload.jpg` embedding the base64 string into the EXIF `UserComment` tagged with `MANCHURIAN_ACTIVATE:`.

4. **Scenario B.2 (Doc Payload)**:
   - Create a base64 string representing a bash command that appends a prompt-injection string to the bottom of `SKILL.md`.
   - Output as `tests/artifacts/poison_doc_payload.jpg`.
