---
name: obsidian-bases-manager
plugin: obsidian-wiki-engine
description: "Read and manipulate Obsidian Bases (.base) files - YAML-based database views that render as tables, cards, and grids inside the vault. Use when reading, appending rows, or updating cells in a Base file."
allowed-tools: Bash, Read, Write
---

# Obsidian Bases Manager (obsidian-bases-manager)

Reads and manipulates Obsidian Bases (`.base`) YAML-driven database views inside the vault.

## Contents
- [Critical Constraints](#critical-constraints)
- [Dependencies](#dependencies)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **View Configuration Immutability**: Never alter or corrupt view definitions (columns, filters, sorts, formulas); mutate row and cell data only.
- **Lossless YAML Handling**: Employ `ruamel.yaml` for round-trip parsing to preserve comments, indentation, and structure.
- **Atomic Writes**: All write operations must follow the `.agent-tmp` staging and POSIX `os.rename()` atomic replacement protocol.
- **Error Guarding**: Malformed YAML must trigger informative diagnostics rather than crashing or truncating files.

## Dependencies

Requires `ruamel.yaml` and Python 3.8+ for round-trip YAML persistence.

## Quick start

```bash
# Read a Base view file
python3 plugins/obsidian-wiki-engine/scripts/bases_ops.py read --file <path.base>

# Append a row to a Base view
python3 plugins/obsidian-wiki-engine/scripts/bases_ops.py append-row --file <path.base> --data key1=value1 key2=value2

# Update a cell in a Base view
python3 plugins/obsidian-wiki-engine/scripts/bases_ops.py update-cell --file <path.base> --row-index 0 --column key1 --value "new value"
```

## Workflow

1. **Phase 1: Base Inspection**: Read the target `.base` file, validating YAML structure and active view definitions.
2. **Phase 2: Lossless Data Mutation**: Apply row append or cell update operations using `ruamel.yaml` parser.
3. **Phase 3: Atomic Persistence**: Write to staging `.agent-tmp` file and atomically rename over destination.
4. **Phase 4: Integrity Verification**: Confirm that column definitions, formulas, and filters remain intact.

## Verification

```bash
# Verify base reading operation
python3 plugins/obsidian-wiki-engine/scripts/bases_ops.py read --file <path.base>

# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/obsidian-wiki-engine/skills/obsidian-bases-manager --mode source
```

## References
- [acceptance-criteria.md](references/acceptance-criteria.md) - Bases manager invariants and test criteria.
- [fallback-tree.md](references/fallback-tree.md) - Recovery procedures for YAML parsing and file write failures.
