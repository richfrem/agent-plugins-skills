---
name: obsidian-markdown-mastery
plugin: obsidian-wiki-engine
description: "Core markdown syntax skill for Obsidian. Enforces strict parsing and authoring of Obsidian proprietary syntax (Wikilinks, Blocks, Headings, Aliases, Embeds, Callouts). Use when reading, writing, or validating Obsidian-flavored markdown."
allowed-tools: Bash, Read, Write
---

# Obsidian Markdown Mastery (obsidian-markdown-mastery)

Enforces deterministic parsing, formatting, and validation of Obsidian-flavored Markdown syntax.

## Contents
- [Critical Constraints](#critical-constraints)
- [Dependencies](#dependencies)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Deterministic Python Parsing**: All link and block extraction must execute via the `obsidian-parser` module rather than ad-hoc regex.
- **Protocol Agnosticism**: The parser remains decoupled from project-specific workflows, operating solely on markdown text and AST tokens.
- **Proprietary Syntax Integrity**: Enforce exact syntax rules for wikilinks (`[[Note#Heading|Alias]]`), block IDs (`^block-id`), and callouts (`> [!type]`).
- **Vault Root Discovery**: Use `OBSIDIAN_VAULT_PATH` environment variable for root discovery, defaulting safely to repository root.

## Dependencies

Requires `obsidian-parser` and Python 3.8+ (standard library only).

## Quick start

```bash
# Extract links, embeds, and block metadata from note
python3 plugins/obsidian-wiki-engine/scripts/obsidian-parser/parser.py analyze --file <path_to_md>

# Construct an Obsidian callout block
python3 plugins/obsidian-wiki-engine/scripts/obsidian-parser/parser.py callout --type info --title "Notice" --text "Body"
```

## Workflow

1. **Phase 1: Text Ingestion & Tokenizing**: Parse target markdown files using `parser.py` to identify AST components.
2. **Phase 2: Metadata Extraction**: Segregate semantic wikilinks (`[[Link]]`) from embeds (`![[Embed]]`) and block references (`^id`).
3. **Phase 3: Syntax Authoring**: Apply deterministic formatting primitives when generating new notes or inserting callouts.
4. **Phase 4: Downstream Handoff**: Supply parsed metadata to graph traversers and vault indexers.

## Verification

```bash
# Verify parser CLI execution
python3 plugins/obsidian-wiki-engine/scripts/obsidian-parser/parser.py analyze --help

# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/obsidian-wiki-engine/skills/obsidian-markdown-mastery --mode source
```

## References
- [acceptance-criteria.md](references/acceptance-criteria.md) - Syntax compliance and parsing criteria.
- [fallback-tree.md](references/fallback-tree.md) - Recovery procedures for malformed markdown or broken wikilinks.
