---
concept: acceptance-criteria-mermaid-to-png-converter
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/convert-mermaid/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.752830+00:00
cluster: must
content_hash: 092bfc3c8ab2236e
---

# Acceptance Criteria: Mermaid To PNG Converter

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: Mermaid To PNG Converter

The `mermaid-to-png` workflow MUST satisfy the following success metrics:

1. **Successful Binary Generation**: Given an `.mmd` file, the command successfully triggers the Python wrapper to generate a `.png` via headless browser.
2. **Delegated Constraint Pass**: The output `.png` must pass entirely through `../scripts/verify_png.py` returning `"status": "success"` with 0 MissingMagicBytes.
3. **Context Window Safety**: The agent must NEVER attempt to print or `cat` massive generated `.png` binaries into the context window to verify their existence.


## See Also

- [[acceptance-criteria-excel-to-csv-converter]]
- [[acceptance-criteria-markdown-to-word-converter]]
- [[acceptance-criteria-excel-to-csv-converter]]
- [[acceptance-criteria-excel-to-csv-converter]]
- [[acceptance-criteria-markdown-to-word-converter]]
- [[acceptance-criteria-markdown-to-word-converter]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/convert-mermaid/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:09.752830+00:00
