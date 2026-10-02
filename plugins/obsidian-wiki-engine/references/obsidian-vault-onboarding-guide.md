# Obsidian Vault Onboarding & Initialization Guide

## Contents
- [Prerequisites Installation](#prerequisites-installation)
- [Vault Initialization](#vault-initialization)
- [Exclusion Configuration](#exclusion-configuration)
- [Post-Init Verification](#post-init-verification)
- [Wiki Engine Guided Discovery](#wiki-engine-guided-discovery)
- [Portability & Quick Reference](#portability--quick-reference)

---

## Prerequisites Installation

### 1. Obsidian Desktop Application (Required)
The Obsidian desktop app must be installed on the host machine as the visual interface for browsing, editing, and viewing the Graph and Canvas.

- **macOS (Homebrew):**
  ```bash
  brew install --cask obsidian
  ```
- **Manual Download:** https://obsidian.md/download
- **Verify:**
  ```bash
  ls /Applications/Obsidian.app
  ```

### 2. Obsidian CLI v1.12+ (Recommended)
Communicates with running Obsidian instance via IPC lock for programmatic vault operations.

- **npm (global install):**
  ```bash
  npm install -g obsidian-cli
  ```
- **Verify:**
  ```bash
  obsidian --version
  ```

### 3. ruamel.yaml
Required for lossless YAML frontmatter parsing and preservation:
```bash
pip install ruamel.yaml
```

### 4. Optional Community Plugins
- **Dataview:** Structured database-style queries over frontmatter metadata.
- **Canvas:** Built-in visual boards adhering to JSON Canvas Spec 1.0.
- **Bases:** Table, grid, and card views from YAML properties.

---

## Vault Initialization

### Command Execution
```bash
# Interactive initialization
python ./init_vault.py --vault-root <path>

# With custom exclusions
python ./init_vault.py --vault-root <path> --exclude "custom_dir/" "*.tmp"

# Dry run validation only
python ./init_vault.py --vault-root <path> --validate-only
```

### Initialization Actions
1. **Validates** directory exists and contains markdown files.
2. **Creates** `.obsidian/` configuration directory.
3. **Writes** `app.json` with sensible developer defaults.
4. **Updates** `.gitignore` to exclude `.obsidian/`.
5. **Reports** next steps for opening vault in Obsidian desktop.

---

## Exclusion Configuration

### Default Exclusions
| Pattern | Reason |
|:--------|:-------|
| `node_modules/` | NPM dependencies |
| `.worktrees/` | Git worktree isolation |
| `.vector_data/` | ChromaDB binary storage |
| `.git/` | Git internal metadata |
| `venv/`, `.venv/` | Python virtual environments |
| `__pycache__/` | Python bytecode cache |
| `*.json`, `*.jsonl` | Data payloads and export bundles |
| `*_packet.md`, `*_digest.md` | Machine-generated context bundles |

*Rationale:* Machine-generated files create thousands of false backlinks and pollute graph connectivity.

---

## Post-Init Verification

1. Open Obsidian -> "Open Folder as Vault" -> select vault root.
2. Verify indexing: Confirm structural folders appear in sidebar.
3. Test wikilinks: Click `[[wikilink]]` references to confirm bidirectional resolution.
4. Set environment variable: `export VAULT_PATH=/path/to/vault`.

---

## Wiki Engine Guided Discovery

After vault initialization, configure the LLM Wiki Engine source manifest (`rlm_wiki_raw_sources_manifest.json`):

### Running Discovery
```bash
python ./scripts/raw_manifest.py --init --wiki-root /path/to/wiki-root
```

### Manifest Schema
```json
{
  "description": "Source raw content for Obsidian Wiki",
  "include": [
    "plugins/",
    "docs/"
  ],
  "exclude": [
    ".git/",
    "node_modules/",
    ".venv/",
    "__pycache__/"
  ],
  "recursive": true
}
```

---

## Portability & Quick Reference

```bash
# 1. Install prerequisites
brew install --cask obsidian
npm install -g obsidian-cli
pip install ruamel.yaml

# 2. Initialize vault
python ./init_vault.py --vault-root /path/to/your/project

# 3. Export environment
export VAULT_PATH=/path/to/your/project
```
