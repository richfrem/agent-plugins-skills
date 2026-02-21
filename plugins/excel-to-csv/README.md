# Excel To Csv Plugin 📊

Convert Excel files (entire workbooks or specific worksheets/tables) into CSV format natively via agent execution.

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
├── scripts/convert.py
└── README.md
```

## Usage
The skill is invoked automatically. Claude will use the local `scripts/convert.py` to flatten your `.xlsx` data into accessible tabular CSV data for easier text processing.
