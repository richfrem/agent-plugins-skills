---
concept: excel-to-csv-plugin-v2
source: plugin-code
source_file: excel-to-csv/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.558128+00:00
cluster: agent
content_hash: 79b5e51c87fc19e8
---

# Excel To Csv Plugin 📊 (V2)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Excel To Csv Plugin 📊 (V2)

Convert Excel files (entire workbooks or specific worksheets/tables) into CSV format natively via agent execution. Upgraded to V2 with L5 Delegated Constraint Verification.

## Structure
```
excel-to-csv/
├── .claude-plugin/plugin.json
├── skills/excel-to-csv/SKILL.md
├── skills/excel-to-csv/scripts/convert.py
├── skills/excel-to-csv/scripts/verify_csv.py
├── skills/excel-to-csv/references/
└── README.md
```

## Usage
The skill is invoked automatically. The agent will use the local `scripts/convert.py` to flatten your `.xlsx` data, and will immediately run the generated output through `scripts/verify_csv.py`. This strict L5 Delegated Constraint Loop ensures no jagged rows or corrupt headers are generated before the agent analyzes the tabular CSV data.

## Plugin Components

### Skills
- `excel-to-csv`

### Scripts
- `scripts/convert.py`
- `scripts/verify_csv.py`



## See Also

- [[acceptance-criteria-excel-to-csv-converter]]
- [[acceptance-criteria-excel-to-csv-converter]]
- [[acceptance-criteria-excel-to-csv-converter]]
- [[acceptance-criteria-audit-plugin-l5nndefine-at-least-two-testable-criteria-or-correctincorrect-operational-patterns-here-to-ensure-the-skill-functions-correctly]]
- [[markdown-to-msword-converter-v2]]
- [[mermaid-to-png-plugin]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `excel-to-csv/README.md`
- **Indexed:** 2026-04-17T06:42:09.558128+00:00
