# Acceptance Criteria: Markdown To Word Converter

The `markdown-to-msword-converter` workflow MUST satisfy the following success metrics:

1. **Successful Binary Extraction**: Given an `.md` file or batch config, the command successfully triggers the Python scripts to generate standalone `.docx` files.
2. **Delegated Constraint Pass**: The output `.docx` must pass entirely through `./verify_docx.py` returning `"status": "success"` with 0 ArchiveCorrupt or NoParagraphs errors.
3. **Context Window Safety**: The agent must NEVER attempt to print, build, or `cat` massive generated `.docx` ZIP archives into the context window.
