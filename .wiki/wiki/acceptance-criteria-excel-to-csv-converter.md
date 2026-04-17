---
concept: acceptance-criteria-excel-to-csv-converter
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/excel-to-csv/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.076077+00:00
cluster: must
content_hash: 0dc5f70534abb73e
---

# Acceptance Criteria: Excel To CSV Converter

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: Excel To CSV Converter

The `excel-to-csv` workflow MUST satisfy the following success metrics:

1. **Successful Binary Extraction**: Given a multi-sheet `.xlsx` file, the command successfully triggers `../scripts/convert.py` to extract designated sheets into separate `.csv` files inside an output directory.
2. **Delegated Constraint Pass**: The output `.csv` must pass entirely through `../scripts/verify_csv.py` returning `"status": "success"` with 0 jagged rows or empty bounds.
3. **Context Window Safety**: The agent must NEVER attempt to print or `cat` massive generated `.csv` files into the context window, strictly obeying the `head` truncation rule for files > 50 lines.


## See Also

- [[acceptance-criteria-markdown-to-word-converter]]
- [[acceptance-criteria-mermaid-to-png-converter]]
- [[acceptance-criteria-mermaid-to-png-converter]]
- [[acceptance-criteria-mermaid-to-png-converter]]
- [[acceptance-criteria-markdown-to-word-converter]]
- [[acceptance-criteria-markdown-to-word-converter]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/excel-to-csv/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.076077+00:00
