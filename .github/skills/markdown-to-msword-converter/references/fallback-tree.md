# Procedural Fallback Tree: Markdown to MS Word Conversion

If the primary Conversion Engine (`md_to_docx.py`) or the Delegate Constraints (`verify_docx.py`) fail, execute the following triage steps exactly in order:

## 1. Engine Execution Failure (ImportError / Env Issues)
If script crashes due to missing dependencies (`pypandoc`, `markdown`, `docx`):
- **Action**: Check if standard python dependencies were installed via the `requirements.in`. Provide the pip install command to the user.

## 2. Parsing Error (Missing Pandoc Binary)
If the `.py` script complains that the underlying native `pandoc` binary is missing from the system:
- **Action**: Inform the user they must install the system-level Pandoc tool (e.g., `brew install pandoc` or `apt-get install pandoc`), as `pypandoc` is just a Python wrapper over the native C engine. Do not attempt to write a Python-only markdown parser from scratch.

## 3. Verification Loop Rejection (ArchiveCorrupt)
If `verify_docx.py` returns `ArchiveCorrupt`:
- **Action**: Document creation failed entirely. Check the original `.md` file for complex or broken HTML tags (e.g., mismatched `<div>` or `<style>` blocks) that the parser choked on. Offer to strip raw HTML from the source `.md` file and retry.

## 4. Verification Loop Rejection (NoParagraphs)
If `verify_docx.py` returns `NoParagraphs` but the file assembled successfully:
- **Action**: The source file was either completely empty, or it only contained elements the parser decided to skip (like hidden YAML frontmatter). Check the source file's contents before retrying.
