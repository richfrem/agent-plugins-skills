---
name: rlm-init
description: "Interactive RLM cache initialization. Use when: setting up a new project's semantic cache for the first time, or adding a new cache profile. Walks the user through folder selection, extension config, manifest creation, and first distillation pass."
---

# RLM Init: Cache Bootstrap

Initialize a new RLM semantic cache for any project. This is the **first-run** workflow — run it once per cache, then use `rlm-distill` for ongoing updates.

## When to Use

- First time using RLM Factory in a project
- Adding a new cache profile (e.g., separate cache for API docs vs scripts)
- Rebuilding a cache from scratch after major restructuring

## Interactive Setup Protocol

### Step 1: Ask the User

Before creating anything, gather requirements:

1. **"What do you want cached?"** — What kind of files? (docs, scripts, configs, etc.)
2. **"Which folders should be included?"** — (e.g., `docs/`, `src/`, `plugins/`)
3. **"Which file extensions?"** — (e.g., `.md`, `.py`, `.ts`)
4. **"Where should the cache live?"** — Default: `.agent/learning/`
5. **"What should we name this cache?"** — (e.g., `plugins`, `project`, `tools`)

### Step 2: Configure `.env`

Each cache is defined by 3 `.env` entries. Append to the project's `.env` file:

```bash
# ── RLM Cache: <NAME> ────────────────────────────
RLM_<NAME>_MANIFEST=.agent/learning/<name>_manifest.json
RLM_<NAME>_CACHE=.agent/learning/rlm_<name>_cache.json
RLM_<NAME>_EXTENSIONS=.md,.py,.ts
```

| Variable | Purpose |
|----------|---------|
| `RLM_<NAME>_MANIFEST` | Path to the manifest JSON (what folders/files to index) |
| `RLM_<NAME>_CACHE` | Path to the cache JSON (where summaries are stored) |
| `RLM_<NAME>_EXTENSIONS` | Comma-separated file extensions to include |

```bash
mkdir -p .agent/learning
```

### Step 3: Create the Manifest

The manifest defines **which folders and files** to index. Extensions come from `.env`.

Create `<manifest_path>`:
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

### Step 4: Initialize Empty Cache

```bash
echo "{}" > <cache_path>
```

### Step 5: Audit (Show What Needs Caching)

Scan the manifest against the cache to find uncached files:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm-curator/scripts/inventory.py
```

Report: "N files in manifest, M already cached, K remaining."

### Step 6: Serial Agent Distillation

For each uncached file:
1. **Read** the file
2. **Summarize** — Generate a concise, information-dense summary
3. **Write** the summary into the cache JSON with this schema:

```json
{
  "<relative_path>": {
    "hash": "agent_distilled_<YYYY_MM_DD>",
    "summary": "<your summary>",
    "summarized_at": "<ISO timestamp>"
  }
}
```

4. **Log**: `"✅ Cached: <path>"`
5. **Repeat** for next file

### Step 7: Verify

Run audit again:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm-curator/scripts/inventory.py
```

Target: 100% coverage. If gaps remain, repeat Step 6 for missing files.

## Quality Guidelines

Every summary should answer: **"Why does this file exist and what does it do?"**

| ❌ Bad | ✅ Good |
|--------|---------|
| "This is a README file" | "Plugin providing 5 composable agent loop patterns for learning, red team review, dual-loop delegation, and parallel swarm execution" |
| "Contains a SKILL definition" | "Orchestrator skill that routes tasks to the correct loop pattern using a 4-question decision tree, manages shared closure sequence" |

## After Init

- Use [`rlm-distill`](../rlm-distill/SKILL.md) for ongoing cache updates
- Use [`rlm-curator`](../rlm-curator/SKILL.md) for querying, auditing, and cleanup
- Cache files should be `.gitignore`d if they contain project-specific summaries
