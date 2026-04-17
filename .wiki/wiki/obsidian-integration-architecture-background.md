---
concept: obsidian-integration-architecture-background
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/obsidian-vault-crud/assets/resources/architecture-background.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.131001+00:00
cluster: files
content_hash: 6270088e7a00e46f
---

# Obsidian Integration: Architecture Background

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Obsidian Integration: Architecture Background

## Why Direct Filesystem (Zero-RPC)?

After evaluating three integration strategies (see ADR 099), the direct filesystem
read/write approach was chosen over Obsidian's Local REST API and custom TypeScript plugins.

### Strategies Evaluated

| Strategy | Pros | Cons | Verdict |
|:---------|:-----|:-----|:--------|
| **Local REST API** | Clean HTTP interface | Requires Obsidian running; extra dependency | ❌ Rejected |
| **Custom TypeScript Plugin** | Deep Obsidian integration | Requires TypeScript build chain; brittle | ❌ Rejected |
| **Direct Filesystem** | Zero dependencies; works offline | No real-time sync | ✅ Chosen |

### Rationale
- **Zero Dependencies**: No running Obsidian instance required for agents to operate
- **Offline-First**: Agents can read/write vault files without any server
- **Git-Native**: Files are plain markdown tracked by Git — no proprietary format
- **Portability**: This plugin works on any project with `.md` files

## Key Architectural Principles

### 1. Agnosticism
The Obsidian skills know NOTHING about any specific project's domain logic.
They only know how to parse/write Obsidian-flavored markdown. Project-specific
context (like which folders map to what) is injected by the project's own
configuration (e.g., `VAULT_PATH`).

### 2. Separation of Concerns
```
obsidian-markdown-mastery  → Syntax parsing (wikilinks, embeds, callouts)
obsidian-vault-crud        → Safe disk I/O (atomic writes, locking, mtime)
obsidian-init              → Vault bootstrapping and configuration
```

The parser never touches disk. The CRUD layer never parses syntax. Each skill has exactly one job.

### 3. Safety-First Writes
All file mutations use:
- **Atomic writes** via POSIX `os.rename()` from `.agent-tmp` staging files
- **Advisory locking** via `.agent-lock` at the vault root
- **Concurrent edit detection** via `mtime` comparison before/after operations
- **Lossless YAML** via `ruamel.yaml` (never PyYAML) for frontmatter

## Obsidian Vault Basics

An Obsidian Vault is simply a folder on disk. There is no database, no server,
no proprietary format. Obsidian reads `.md` files and builds its graph view,
backlinks, and search index from the raw text.

### Key Obsidian Syntax
- `[[Note Name]]` — Internal link (wikilink)
- `[[Note#Heading]]` — Link to a specific heading
- `[[Note#^block-id]]` — Link to a specific block
- `[[Note|Display Text]]` — Aliased link
- `![[Note]]` — Transclusion/embed (note the `!` prefix)
- `> [!type] Title` — Callout blocks

### Configuration
- `.obsidian/` — Local config directory (should be `.gitignore`d)
- `.obsidian/app.json` — App settings including `userIgnoreFilters`
- Frontmatter (YAML between `---` delimiters) — Metadata for Dataview and Properties


## See Also

- [[triple-loop-learning-system---architecture-overview]]
- [[agentic-os-architecture]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[autoresearch-architecture]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[triple-loop-learning-system---architecture-overview]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/obsidian-vault-crud/assets/resources/architecture-background.md`
- **Indexed:** 2026-04-17T06:42:10.131001+00:00
