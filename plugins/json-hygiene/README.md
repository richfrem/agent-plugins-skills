# JSON Hygiene Plugin (V2) 🧹

Safeguard your JSON configuration files against silent data loss caused by duplicate keys.

## Features
- **Deterministic AST Detection**: Hook into the Python JSON parser (`object_pairs_hook`) to intercept the AST. Catches 100% of duplicate keys (the "last-one-wins" flaw) across all nesting depths.
- **Manifest Validation**: Designed to audit complex nested configuration structures.

## Installation

### Local Development
```bash
claude --plugin-dir ./plugins/json-hygiene
```

## Usage

### CLI
```bash
# Check a single file
python3 ./scripts/find_json_duplicates.py --file plugins/tool_inventory.json
```

### Agent Integration
Invoke the **json-hygiene-agent** by asking:
> "Check this manifest for duplicates."
> "Audit my JSON configs."

## Directory Structure
```
json-hygiene/
├── scripts/
│   └── find_json_duplicates.py   # The regex scanner
├── skills/
│   └── json-hygiene-agent/
│       └── SKILL.md              # Agent persona
└── README.md
```

## License
MIT
