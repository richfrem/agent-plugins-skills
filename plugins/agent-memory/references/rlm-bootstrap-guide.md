# RLM Bootstrap Guide

Detailed interactive configuration and setup protocol for initializing a Recursive Language Model (RLM) semantic cache.

## Contents
- [Step 0: Setup Mode Selection](#step-0-setup-mode-selection)
- [Step 1: Requirements Gathering](#step-1-requirements-gathering)
- [Step 2: Profile Configuration](#step-2-profile-configuration)
- [Step 3: Manifest Creation](#step-3-manifest-creation)
- [Step 4: Directory Initialization](#step-4-directory-initialization)
- [Step 5: Cache Audit](#step-5-cache-audit)
- [Step 6: Distillation Workflow](#step-6-distillation-workflow)
- [Step 7: Verification](#step-7-verification)
- [Quality Guidelines](#quality-guidelines)

---

## Step 0: Setup Mode Selection

Before starting, check installed plugins:
```bash
ls .agents/skills/vector-db-init/ 2>/dev/null && echo "vector-db: INSTALLED" || echo "vector-db: NOT FOUND"
ls .agents/skills/obsidian-wiki-builder/ 2>/dev/null && echo "obsidian-wiki-engine: INSTALLED" || echo "obsidian-wiki-engine: NOT FOUND"
```

Select a setup mode:
- **Mode A (Standalone):** RLM only. O(1) keyword search across dense file summaries. Zero external dependencies.
- **Mode B (RLM + vector-db):** RLM keyword pre-filter into vector semantic search.
- **Mode C (RLM + obsidian-wiki-engine):** RLM as wiki concept distiller.
- **Mode D (Super-RAG):** All three layers: RLM keyword -> vector semantic -> wiki concept nodes.

---

## Step 1: Requirements Gathering

Gather target scope:
1. Target content: docs, scripts, plugins, configuration files.
2. Target directories: e.g. `docs/`, `src/`, `plugins/`.
3. Target file extensions: e.g. `.md`, `.py`, `.ts`.
4. Cache directory: default `.agent/learning/` or `config/rlm/`.
5. Profile name: e.g. `project`, `tools`, `wiki`.

---

## Step 2: Profile Configuration

Create or append to `<profiles_dir>/rlm_profiles.json` (defaults to `.agent/learning/rlm_profiles.json`):

```json
{
  "version": 1,
  "default_profile": "<NAME>",
  "profiles": {
    "<NAME>": {
      "description": "<What this cache contains>",
      "manifest": "<profiles_dir>/<name>_manifest.json",
      "cache": "<profiles_dir>/rlm_<name>_cache.json",
      "extensions": [
        ".md",
        ".py",
        ".ts"
      ]
    }
  }
}
```

| Key | Purpose |
|---|---|
| `description` | Human-readable explanation of profile scope |
| `manifest` | Path to manifest JSON listing include/exclude globs |
| `cache` | Path to cache directory location |
| `extensions` | List of file extensions to include |

---

## Step 3: Manifest Creation

Create `<profiles_dir>/<name>_manifest.json`:
```json
{
  "description": "<What this cache contains>",
  "include": [
    "<folder_or_glob_1>",
    "<folder_or_glob_2>"
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

## Step 4: Directory Initialization

Ensure cache directories exist on disk:
```bash
mkdir -p .agent/learning
```
No database setup is needed because summaries persist directly to markdown files.

---

## Step 5: Cache Audit

Scan manifest against cache to identify uncached files:
```bash
python ./scripts/inventory.py --profile <NAME>
```

Report: "N files in manifest, M already cached, K remaining."

---

## Step 6: Distillation Workflow

For each uncached file:
1. Read file completely with `view_file`.
2. Generate dense 1-sentence summary answering purpose and key components.
3. Inject summary via script:
   ```bash
   python ./scripts/inject_summary.py --profile <NAME> --file <PATH> --summary "<SUMMARY>"
   ```

---

## Step 7: Verification

Verify 100% cache coverage:
```bash
python ./scripts/inventory.py --profile <NAME>
```

---

## Quality Guidelines

Every summary should answer: **"Why does this file exist and what does it do?"**

| Bad | Good |
|---|---|
| "This is a README file" | "Plugin providing 5 composable agent loop patterns for learning, red team review, and parallel swarms." |
| "Contains a SKILL definition" | "Orchestrator skill routing tasks to loop patterns using a 4-question decision tree." |
