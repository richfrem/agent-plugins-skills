---
concept: procedural-fallback-tree-markdown-to-ms-word-conversion
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/markdown-to-msword-converter/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.116623+00:00
cluster: file
content_hash: 1b11203b102d6bda
---

# Procedural Fallback Tree: Markdown to MS Word Conversion

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Markdown to MS Word Conversion

If the primary Conversion Engine (`../scripts/md_to_docx.py`) or the Delegate Constraints (`./../scripts/verify_docx.py`) fail, execute the following triage steps exactly in order:

## 1. Engine Execution Failure (ImportError / Env Issues)
If script crashes due to missing dependencies (`pypandoc`, `markdown`, `docx`):
- **Action**: Check if standard python dependencies were installed via the `../../../requirements.in`. Provide the pip install command to the user.

## 2. Parsing Error (Missing Pandoc Binary)
If the `.py` script complains that the underlying native `pandoc` binary is missing from the system:
- **Action**: Inform the user they must install the system-level Pandoc tool (e.g., `brew install pandoc` or `apt-get install pandoc`), as `pypandoc` is just a Python wrapper over the native C engine. Do not attempt to write a Python-only markdown parser from scratch.

## 3. Verification Loop Rejection (ArchiveCorrupt)
If `./../scripts/verify_docx.py` returns `ArchiveCorrupt`:
- **Action**: Document creation failed entirely. Check the original `.md` file for complex or broken HTML tags (e.g., mismatched `<div>` or `<style>` blocks) that the parser choked on. Offer to strip raw HTML from the source `.md` file and retry.

## 4. Verification Loop Rejection (NoParagraphs)
If `./../scripts/verify_docx.py` returns `NoParagraphs` but the file assembled successfully:
- **Action**: The source file was either completely empty, or it only contained elements the parser decided to skip (like hidden YAML frontmatter). Check the source file's contents before retrying.


## See Also

- [[procedural-fallback-tree-mermaid-to-png-conversion]]
- [[procedural-fallback-tree-mermaid-to-png-conversion]]
- [[procedural-fallback-tree-mermaid-to-png-conversion]]
- [[procedural-fallback-tree-context-bundler-markdown]]
- [[procedural-fallback-tree-excel-conversion]]
- [[identity-the-markdown-to-ms-word-converter]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/markdown-to-msword-converter/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.116623+00:00
