# Acceptance Criteria: Mermaid To PNG Converter

The `mermaid-to-png` workflow MUST satisfy the following success metrics:

1. **Successful Binary Generation**: Given an `.mmd` file, the command successfully triggers the Python wrapper to generate a `.png` via headless browser.
2. **Delegated Constraint Pass**: The output `.png` must pass entirely through `../scripts/verify_png.py` returning `"status": "success"` with 0 MissingMagicBytes.
3. **Context Window Safety**: The agent must NEVER attempt to print or `cat` massive generated `.png` binaries into the context window to verify their existence.
