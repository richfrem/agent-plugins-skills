# Link Checker Plugin 🔗

Validate and auto-repair broken documentation links across your repository using
file inventory mapping and unique-basename matching.

## Installation

### Local Development
```bash
claude --plugin-dir ./plugins/link-checker
```

### From Marketplace (when published)
```
/plugin install link-checker
```

### Prerequisites
- **Claude Code** ≥ 1.0.33
- **Python** ≥ 3.8 (stdlib only — no pip dependencies)

### Verify Installation
With native plugins enabled, your agent autonomously detects the task and executes the required python scripts.

---

## Usage Guide

The autonomous agent executes a strict **5-Step Pipeline**: **Inventory → Extract → Audit → Fix → Report**

### Tell your agent:
```text
"Run the link checker to fix any broken documentation paths."
"Move docs/auth.md to docs/api/auth.md and run the link checker."
```

### Direct CLI Usage (without an Agent)
```bash
cd /path/to/your/repo

# Step 1: Build file inventory
python3 ./scripts/01_build_file_inventory.py

# Step 2: Extract all link references
python3 ./scripts/02_extract_link_references.py

# Step 3: Audit — identify broken links
python3 ./scripts/03_audit_broken_links.py

# Step 4: Auto-fix unique matches (preview first)
python3 ./scripts/04_autofix_unique_links.py --dry-run
python3 ./scripts/04_autofix_unique_links.py --backup

# Step 5: Report remaining unfixable links
python3 ./scripts/05_report_unfixable_links.py
```

### How the Fixer Works

1. Scans `.md` files for `[text](broken/path)` and `![alt](broken/image)` patterns
2. Extracts the basename from broken paths
3. Looks up the basename in `file_inventory.json`
4. **Unique match** → rewrites with correct relative path
5. **Ambiguous** (multiple files with same name) → skips with warning
6. **Not found** → left as-is; appears in `unfixable_links_report.md`

### Safety Features
- Use `--dry-run` to preview all changes before any file is modified
- Use `--backup` to create `.bak` copies before modifying files
- Only modifies files listed in `broken_links.json` (from Step 3)
- Skips `README.md` basename matches (too ambiguous across repos)
- Preserves anchor fragments (`#section`)
- Skips links inside fenced code blocks
- Excludes `.git`, `node_modules`, `.venv`, `bin`, `obj` from scanning

---

## Architecture

See [workflow diagram](assets/diagrams/workflow.mmd) for the full 5-step flow.

```mermaid
graph LR
    A["Inventory 🗺️"] -->|file_inventory.json| B["Extract 📋"]
    B -->|link_references.json| C["Audit 🔍"]
    C -->|broken_links.json| D["Fix 🔧"]
    D -->|Modified .md files| E["Report 📄"]
    E -->|unfixable_links_report.md| F[Review]
```

Additional diagrams:
- [logic.mmd](assets/diagrams/logic.mmd) — Internal decision logic
- [workflow.mmd](assets/diagrams/workflow.mmd) — User workflow
- [link-checker-workflow.mmd](assets/diagrams/link-checker-workflow.mmd) — Full sequence diagram

### Plugin Directory Structure
```
link-checker/
├── .claude-plugin/
│   └── plugin.json              # Plugin identity
├── scripts/
│   ├── 01_build_file_inventory.py   # The Mapper
│   ├── 02_extract_link_references.py # The Extractor
│   ├── 03_audit_broken_links.py     # The Auditor
│   ├── 04_autofix_unique_links.py   # The Fixer
│   └── 05_report_unfixable_links.py # The Reporter
├── skills/
│   └── link-checker-agent/
│       ├── SKILL.md             # Auto-invoked QA skill
│       ├── scripts/             # Symlinks → ../../scripts/
│       └── references/          # Symlinks → ../../references/
└── README.md
```

---

## License

MIT

## Plugin Components

### Skills
- `link-checker-agent`
