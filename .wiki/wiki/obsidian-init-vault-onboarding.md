---
concept: obsidian-init-vault-onboarding
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/obsidian-integration_obsidian-init.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.322944+00:00
cluster: plugin-code
content_hash: 7d2b61505d5a06f7
---

# Obsidian Init (Vault Onboarding)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
| `*_packet

*(content truncated)*

## See Also

- [[huggingface-init-onboarding]]
- [[acceptance-criteria-obsidian-init]]
- [[procedural-fallback-tree-obsidian-init]]
- [[obsidian-vault-crud]]
- [[acceptance-criteria-obsidian-vault-crud]]
- [[procedural-fallback-tree-obsidian-vault-crud]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/obsidian-integration_obsidian-init.md`
- **Indexed:** 2026-04-17T06:42:10.322944+00:00
