# JSON Hygiene Plugin 🧹

Safeguard your JSON configuration files against silent data loss caused by duplicate keys.

## Features
- **Heuristic Duplicate Detection**: Finds duplicate keys that standard parsers ignore (last-one-wins).
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
python3 plugins/json-hygiene/scripts/find_json_duplicates.py --file tools/tool_inventory.json
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
