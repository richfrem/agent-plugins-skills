# Procedural Fallback Tree: Mermaid to PNG Conversion

If the primary Conversion Engine (`././convert.py`) or the Delegate Constraints (`./././verify_png.py`) fail, execute the following triage steps exactly in order:

## 1. Engine Execution Failure (NPM/Node Missing)
If `npx` fails complaining that node or npm are not installed:
- **Action**: Check if standard node dependencies are available on the user's `$PATH`. If not, abort and inform the user they must install Node.js (`brew install node` or `apt-get install nodejs`) to use the headless mermaid renderer.

## 2. Puppeteer Sandbox Sandbox Errors
If the script complains about Chrome sandbox issues (`No usable sandbox! Update your kernel`):
- **Action**: The `././convert.py` script automatically bypasses the sandbox explicitly by creating `puppeteer-config.json` with `{"args": ["--no-sandbox"]}`. Ensure the filesystem permissions allow the python script to create this temporary file.

## 3. Verification Loop Rejection (MissingMagicBytes)
If `./././verify_png.py` returns `MissingMagicBytes`:
- **Action**: The file created was not a PNG image. Often, if there's a syntax error in the `.mmd` file, the Mermaid-CLI catches the error and writes the textual stack trace directly into the target `.png` file instead of creating an image. Read the *contents* of the `.mmd` file to ensure the Mermaid syntax is perfectly valid. Do not attempt to parse the corrupted `.png`.

## 4. Verification Loop Rejection (EmptyFile)
If `./././verify_png.py` returns `EmptyFile`:
- **Action**: The output file is zero bytes. Verify input `.mmd` is not blank.
