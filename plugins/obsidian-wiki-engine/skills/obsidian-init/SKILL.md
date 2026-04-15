---
name: obsidian-init
description: "Initialize and onboard a new project repository as an Obsidian Vault. Covers prerequisite installation, vault configuration, exclusion filters, and validation. Use when setting up Obsidian for the first time in a project."
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
# Obsidian Init (Vault Onboarding)

**Status:** Active
**Author:** Richard Fremmerlid
**Domain:** Obsidian Integration

## Purpose

This skill is the **entry point** for any project adopting Obsidian. It handles:
1. Verifying (and guiding installation of) prerequisites
2. Initializing the vault configuration
3. Setting up exclusion filters
4. Validating the vault is ready for agent operations

---

## Phase 1: Prerequisites Installation

### 1.1 Obsidian Desktop Application (Required)

The Obsidian desktop app must be installed on the host machine. It is the visual
interface for browsing, editing, and viewing the Graph and Canvas.

**macOS (Homebrew):**
```bash
brew install --cask obsidian
```

**Manual Download:**
- https://obsidian.md/download

**Verify:**
```bash
ls /Applications/Obsidian.app
```

### 1.2 Obsidian CLI v1.12+ (Recommended)

The official CLI communicates with a running Obsidian instance via IPC singleton lock.
It enables programmatic vault operations (read, search, backlinks, properties).

**npm (global install):**
```bash
npm install -g obsidian-cli
```

**Verify:**
```bash
obsidian --version
```

> **Note**: The CLI requires an active Obsidian Desktop instance to communicate with.
> It operates in "silent" mode by default. For headless/CI environments where Obsidian
> is not running, our `vault_ops.py` (from `obsidian-vault-crud`) handles direct
> filesystem operations without requiring the CLI.

### 1.3 ruamel.yaml (Required for CRUD Operations)

Lossless YAML frontmatter handling requires `ruamel.yaml`:

```bash
pip install ruamel.yaml
```

### 1.4 Optional Community Plugins

For advanced vault features, install these from within the Obsidian app:

| Plugin | Purpose | Required For |
|:-------|:--------|:-------------|
| **Dataview** | Database-style queries over frontmatter | Structured metadata queries |
| **Canvas** (built-in) | Visual boards with JSON Canvas spec | `obsidian-canvas-architect` skill |
| **Bases** | Table/grid/card views from YAML | `obsidian-bases-manager` skill |

---

## Phase 2: Vault Initialization

### Interactive Init
```bash
python ./init_vault.py --vault-root <path>
```

### With Custom Exclusions
```bash
python ./init_vault.py \
  --vault-root <path> \
  --exclude "custom_dir/" "*.tmp"
```

### Validate Only (No Changes)
```bash
python ./init_vault.py --vault-root <path> --validate-only
```

### What It Does
1. **Validates** the target directory exists and contains `.md` files
2. **Creates** the `.obsidian/` configuration directory (if not present)
3. **Writes** `app.json` with sensible exclusion filters for developer repos
4. **Updates** `.gitignore` to exclude `.obsidian/` (user-specific config)
5. **Reports** next steps for opening the vault in the Obsidian app

---

## Phase 3: Exclusion Configuration

### Default Exclusions

| Pattern | Reason |
|:--------|:-------|
| `node_modules/` | NPM dependencies |
| `.worktrees/` | Git worktree isolation |
| `.vector_data/` | ChromaDB binary data |
| `.git/` | Git internals |
| `venv/` | Python virtual environments |
| `__pycache__/` | Python bytecode cache |
| `*.json` | Data/config files (not knowledge) |
| `*.jsonl` | Export payloads |
| `learning_package_snapshot.md` | Machine-generated bundle |
| `bootstrap_packet.md` | Machine-generated bundle |
| `learning_debrief.md` | Machine-generated bundle |
| `*_packet.md` | Audit/review bundles |
| `*_digest.md` | Context digests |
| `dataset_package/` | Export artifacts |

### Why Exclude Machine-Generated Files?
These are giant concatenated snapshots produced by bundler/distiller scripts.
Indexing them in Obsidian would pollute the graph with thousands of false
backlinks pointing into machine-generated text, not human-authored knowledge.

---

## Phase 4: Post-Init Steps

1. **Open Obsidian** → Click "Open Folder as Vault" → Select vault root
2. **Verify indexing** → Check that `01_PROTOCOLS/`, `ADRs/`, etc. appear in sidebar
3. **Test wikilinks** → Click any `[[link]]` to confirm navigation works
4. **Set VAULT_PATH** → `export VAULT_PATH=/path/to/vault`

---

---

## Phase 5: Wiki Engine Initialization (Guided Discovery Sub-Agent)

After the vault is initialized, you can optionally initialize the **LLM Wiki
Engine** layer. This creates a `wiki_sources.json` manifest — the multi-source
registry that tells the wiki engine which raw content folders to index.

> This is the wiki equivalent of `rlm_profiles.json` in the RLM system.
> Each named entry in `wiki_sources.json` is a raw content directory that
> will be parsed into Karpathy-style wiki nodes. **No files are moved.**

### 5.1 Run the Guided Discovery Sub-Agent

The sub-agent interviews you interactively to register your raw content directories:

```bash
/wiki-init
```

Or directly:
```bash
python ./scripts/raw_manifest.py --init --wiki-root /path/to/wiki-root
```

### 5.2 What the Sub-Agent Asks

For each source folder you want to index, it asks:

| Question | Example Answer |
|:---------|:---------------|
| Wiki root path? | `/path/to/vault/wiki-root` |
| Source folder path? | `/path/to/vault/notes` |
| Label for this source? | `daily-notes` |
| File extensions? | `.md` (default) |
| Subdirectories to exclude? | `_archive, *.tmp` |
| Add another source? | yes/no |

### 5.3 Output: `wiki_sources.json`

```json
{
  "namespace": "my-project",
  "wiki_root": "/path/to/wiki-root",
  "sources": {
    "daily-notes": {
      "path": "/path/to/vault/notes",
      "label": "daily-notes",
      "extensions": [".md"],
      "excludes": ["_archive", "*.tmp"],
      "description": "Daily journal and quick capture notes"
    },
    "arch-docs": {
      "path": "/path/to/docs/architecture",
      "label": "arch-docs",
      "extensions": [".md"],
      "excludes": [],
      "description": "Architecture decision records"
    }
  },
  "global_excludes": ["_archive", "*.tmp", "__pycache__", ".git"]
}
```

### 5.4 Next Steps After Discovery

```bash
/wiki-ingest    ← parse all registered sources, build wiki nodes
/wiki-distill   ← generate RLM summaries (cheapest available LLM CLI)
/wiki-query     ← start querying the wiki
```

> **Requires:** `rlm-factory` plugin installed. See `dependencies.md`.

---

## Portability Note

This skill is **project-agnostic**. It works on any Git repository with markdown
files. The exclusion filters are sensible defaults for developer projects. When
reusing this plugin in other projects, simply run the init script with the new
project's root path.

## Quick Reference: Full Install Sequence

```bash
# 1. Install prerequisites
brew install --cask obsidian        # Desktop app
npm install -g obsidian-cli         # CLI tools
pip install ruamel.yaml             # Lossless YAML

# 2. Initialize vault
python ./init_vault.py \
  --vault-root /path/to/your/project

# 3. Set environment variable
export VAULT_PATH=/path/to/your/project

# 4. Open in Obsidian app
open /Applications/Obsidian.app
```
