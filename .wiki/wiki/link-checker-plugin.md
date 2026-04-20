---
concept: link-checker-plugin
source: plugin-code
source_file: link-checker/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.618340+00:00
cluster: basename
content_hash: 58bf7b4f29d0029b
---

# Link Checker Plugin 🔗

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Link Checker Plugin 🔗

Validate and auto-repair broken documentation links across your repository using
file inventory mapping and unique-basename matching.

## Usage Guide

The autonomous agent executes a strict **5-Step Pipeline**: **Inventory → Extract → Audit → Fix → Report**

### Tell your agent:
```text
"Run the link checker to fix any broken documentation paths."
"Move docs/auth.md to docs/api/auth.md and run the link checker."
```

### Script Location
Scripts live at `./scripts/` in the plugin root. When installed into an agent environment, they are available at `scripts/` relative to the skill directory. Always run from the **repository root** you want to scan.

For installation instructions, consult the authoritative project hub:
> ### 👉 [INSTALL.md](https://github.com/richfrem/agent-plugins-skills/blob/main/INSTALL.md)

### Direct CLI Usage (without an Agent)
```bash
cd /path/to/your/repo

# Full pipeline (one-liner)
python ./scripts/01_build_file_inventory.py && \
python ./scripts/02_extract_link_references.py && \
python ./scripts/03_audit_broken_links.py && \
python ./scripts/04_autofix_unique_links.py --dry-run && \
python ./scripts/04_autofix_unique_links.py --backup && \
python ./scripts/05_report_unfixable_links.py
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


## See Also

- [[identity-the-link-checker]]
- [[acceptance-criteria-link-checker]]
- [[procedural-fallback-tree-link-checker-agent]]
- [[identity-the-link-checker]]
- [[identity-the-link-checker]]
- [[acceptance-criteria-link-checker]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `link-checker/README.md`
- **Indexed:** 2026-04-17T06:42:09.618340+00:00
