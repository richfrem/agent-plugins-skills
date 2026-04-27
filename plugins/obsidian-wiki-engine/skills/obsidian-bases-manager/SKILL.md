---
name: obsidian-bases-manager
plugin: obsidian-wiki-engine
description: "Read and manipulate Obsidian Bases (.base) files - YAML-based database views that render as tables, cards, and grids inside the vault. Use when reading, appending rows, or updating cells in a Base file."
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# Obsidian Bases Manager

**Status:** Active
**Author:** Richard Fremmerlid
**Domain:** Obsidian Integration
**Depends On:** `obsidian-vault-crud` (WP06)

## Purpose

Obsidian Bases are `.base` files containing YAML that defines database-like views
over vault notes. This skill enables agents to act as database administrators —
reading, appending rows, and updating cell values while preserving the view
configuration (columns, filters, sorts) untouched.

## Available Commands

### Read a Base
```bash
python ./bases_ops.py read --file <path.base>
```

### Append a Row
```bash
python ./bases_ops.py append-row --file <path.base> --data key1=value1 key2=value2
```

### Update a Cell
```bash
python ./bases_ops.py update-cell --file <path.base> --row-index 0 --column key1 --value "new value"
```

## Safety Guarantees
- Uses `ruamel.yaml` for lossless round-trip YAML parsing
- All writes go through `obsidian-vault-crud` atomic write protocol
- View configurations (columns, filters, sorts, formulas) are never modified
- Malformed YAML triggers a clean error report, never a crash or data loss
