# Excel To Csv Plugin 📊 (V2)

Convert Excel files (entire workbooks or specific worksheets/tables) into CSV format natively via agent execution. Upgraded to V2 with L5 Delegated Constraint Verification.

## Installation
```bash
claude --plugin-dir ./plugins/excel-to-csv
```

### Dependencies
This plugin requires external Python packages (`pandas`, `openpyxl`). To install them, use the standard dependency management workflow:
```bash
cd plugins/excel-to-csv
pip-compile requirements.in
pip install -r requirements.txt
```

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
