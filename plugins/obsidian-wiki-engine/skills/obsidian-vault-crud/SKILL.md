---
name: obsidian-vault-crud
plugin: obsidian-wiki-engine
description: "Safe Create/Read/Update/Delete operations for Obsidian Vault notes. Implements atomic writes, advisory locking, concurrent edit detection, and lossless YAML frontmatter handling. Use when reading, writing, updating, or appending to any vault note."
allowed-tools: Bash, Read, Write
---

# Obsidian Vault CRUD (obsidian-vault-crud)

Executes safe Create, Read, Update, and Delete operations for vault notes with atomic writes, advisory locking, and conflict detection.

## Contents
- [Critical Constraints](#critical-constraints)
- [Dependencies](#dependencies)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Atomic Write Protocol**: All note updates must stage to `<target>.agent-tmp` before executing atomic POSIX `os.rename()`.
- **Advisory Lock Gate**: Acquire `<vault_root>/.agent-lock` before write batches and release it immediately on completion.
- **Concurrent Edit Detection**: Compare `os.stat(file).st_mtime` before writing; abort if the file changed after reading.
- **Lossless Frontmatter**: Use `ruamel.yaml` to ensure YAML frontmatter, Dataview fields, and property comments are preserved.

## Dependencies

Requires `ruamel.yaml` and Python 3.8+ for atomic file I/O and lossless YAML serialization.

## Quick start

```bash
# Read a vault note
python3 plugins/obsidian-wiki-engine/scripts/vault_ops.py read --file <note-path>

# Create a new note with frontmatter properties
python3 plugins/obsidian-wiki-engine/scripts/vault_ops.py create \
  --file <note-path> --content "Note body" --frontmatter type=concept

# Append content atomically to an existing note
python3 plugins/obsidian-wiki-engine/scripts/vault_ops.py append \
  --file <note-path> --content "\n## Section\nContent"
```

## Workflow

1. **Phase 1: Pre-Flight Lock & Timestamp Check**: Check for `.agent-lock` and record file `st_mtime`.
2. **Phase 2: Frontmatter Isolation**: Parse frontmatter using `ruamel.yaml` to preserve indentation and comments.
3. **Phase 3: Staged Atomic Write**: Write modified content to `<file>.agent-tmp` and atomically rename to destination.
4. **Phase 4: Lock Release & Verification**: Release `.agent-lock` and verify updated note structure.

## Verification

```bash
# Verify vault ops CLI
python3 plugins/obsidian-wiki-engine/scripts/vault_ops.py --help

# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/obsidian-wiki-engine/skills/obsidian-vault-crud --mode source
```

## References
- [acceptance-criteria.md](references/acceptance-criteria.md) - Vault CRUD invariants and atomic safety standards.
- [fallback-tree.md](references/fallback-tree.md) - Stale lock resolution and concurrent conflict handling.
