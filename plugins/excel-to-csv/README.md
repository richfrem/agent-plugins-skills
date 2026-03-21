# Excel To Csv Plugin 📊 (V2)

Convert Excel files (entire workbooks or specific worksheets/tables) into CSV format natively via agent execution. Upgraded to V2 with L5 Delegated Constraint Verification.

## Installation

### Option 1: From a Marketplace (Recommended)
```bash
/plugin marketplace add <marketplace-url>
/plugin install excel-to-csv
```
For skills-only portability across all agents (Claude, Gemini, Copilot, etc.):
```bash
npx skills add <marketplace-url>/plugins/excel-to-csv
```

### Option 2: From GitHub Directly
```bash
# Skills only
npx skills add richfrem/agent-plugins-skills --path plugins/excel-to-csv

# Full plugin (Claude Code native)
/plugin marketplace add richfrem/agent-plugins-skills
/plugin install excel-to-csv
```

### Option 3: Local Development Checkout
```bash
npx skills add ./plugins/excel-to-csv
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

## Plugin Components

### Skills
- `excel-to-csv`

### Scripts
- `scripts/convert.py`
- `scripts/verify_csv.py`

