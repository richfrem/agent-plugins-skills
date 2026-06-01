---
name: rlm-init
plugin: rlm-factory
description: "Interactive RLM cache initialization. Use when: setting up a new project's semantic cache for the first time, or adding a new cache profile. Walks the user through folder selection, extension config, manifest creation, and first distillation pass."
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
# RLM Init: Cache Bootstrap

Initialize a new RLM semantic cache for any project. This is the **first-run** workflow — run it once per cache, then use `rlm-distill-agent` for ongoing updates.

## When to Use

- First time using RLM Factory in a project
- Adding a new cache profile (e.g., separate cache for API docs vs scripts)
- Rebuilding a cache from scratch after major restructuring

## Examples

Real-world examples of each config file are in `references/examples/`:

| File | Purpose |
|:-----|:--------|
| [`manifest-index.json`](resources/manifest-index.json) | Profile registry -- defines named caches and their manifest/cache paths |
| [`rlm_manifest.json`](resources/rlm_manifest.json) | Project docs manifest -- what folders/globs to include and exclude |
| [`distiller_manifest.json`](resources/distiller_manifest.json) | Tools manifest -- scoped to scripts and plugins only |

## Interactive Setup Protocol

### Step 0: Setup Mode Selection

**Ask this before anything else.**

First, check what other plugins are installed:
```bash
ls .agents/skills/vector-db-init/          2>/dev/null && echo "vector-db: INSTALLED"            || echo "vector-db: NOT FOUND"
ls .agents/skills/obsidian-wiki-builder/   2>/dev/null && echo "obsidian-wiki-engine: INSTALLED"  || echo "obsidian-wiki-engine: NOT FOUND"
```

Then ask:
```
RLM Factory works standalone with zero external dependencies. You can also combine it with
other plugins for a more powerful retrieval stack. What setup would you like?

  A) RLM only (standalone)
     - O(1) keyword search across dense file summaries
     - No other plugins needed — works right now

  B) RLM + vector-db Phase 2                          [requires: vector-db in .agents/]
     - RLM keyword pre-filter → vector semantic search
     - Reduces noise, improves precision for large corpora

  C) RLM as wiki distiller                            [requires: obsidian-wiki-engine in .agents/]
     - Generates RLM summary layers per wiki concept node
     - /wiki-query uses RLM Phase 1 before grep

  D) Full Super-RAG                                   [requires: vector-db + obsidian-wiki-engine]
     - All three: RLM keyword → vector semantic → wiki concept nodes

Enter A, B, C, or D (default: A):
```

If required plugins are NOT installed for the chosen mode:
```
[plugin-name] is not installed in .agents/.

To install it:

  # Recommended (uvx — works on Mac, Linux, Windows)
  uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills

  # npx (Mac/Linux)
  npx skills add richfrem/agent-plugins-skills

  # See full install guide
  cat INSTALL.md

After installing, re-run /rlm-factory:init and choose your desired mode.

Continue with Mode A (standalone) for now? (y) or abort and install first? (n)
```

For Mode D, also provision `wiki` and `tools` profiles automatically (see Step 2).

### Step 1: Ask the User

Before creating anything, gather requirements:

1. **"What do you want cached?"** — What kind of files? (docs, scripts, configs, etc.)
2. **"Which folders should be included?"** — (e.g., `docs/`, `src/`, `plugins/`)
3. **"Which file extensions?"** — (e.g., `.md`, `.py`, `.ts`)
4. **"Where should the cache live?"** — Default: `.agent/learning/` or `config/rlm/`
5. **"What should we name this cache?"** — (e.g., `plugins`, `project`, `tools`)

### Step 2: Configure `rlm_profiles.json`

Each cache is defined as a profile in `rlm_profiles.json`. This file is located at `RLM_PROFILES_PATH` or defaults to `.agent/learning/rlm_profiles.json`. If it doesn't exist, create it:

```bash
mkdir -p <profiles_dir>
```

Create or append to `<profiles_dir>/rlm_profiles.json`:

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
|----------|---------|
| `description` | Human-readable explanation of the profile's purpose |
| `manifest` | Path to the manifest JSON (what folders/files to index) |
| `cache` | Path to the cache directory location |
| `extensions` | List of string file extensions to include |

### Step 3: Create the Manifest

The manifest defines **which folders, files, and globs** to index. Extensions come from the profile config.

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

### Step 4: Initialize Config

Make sure that the paths configured in `rlm_profiles.json` are properly created and empty arrays match where required. No `.json` databases are needed because the cache persists directly to `.md` files in a directory.

### Step 5: Audit (Show What Needs Caching)

Scan the manifest against the cache to find uncached files:
```bash
python ./scripts/inventory.py --profile <NAME>
```

Report: "N files in manifest, M already cached, K remaining."

### Step 6: Serial Agent Distillation

For each uncached file:
1. **Read** the file
2. **Summarize** — Generate a concise, information-dense summary
3. **Write** the summary into the cache using the script, which produces this markdown structure natively:

```markdown
---
hash: "agent_distilled_<YYYY_MM_DD>"
summarized_at: "<ISO timestamp>"
---

# Summary
<your summary>
```

4. **Log**: `"✅ Cached: <path>"`
5. **Repeat** for next file

### Step 7: Verify

Run audit again:
```bash
python ./scripts/inventory.py --profile <NAME>
```

Target: 100% coverage. If gaps remain, repeat Step 6 for missing files.

## Quality Guidelines

Every summary should answer: **"Why does this file exist and what does it do?"**

| ❌ Bad | ✅ Good |
|--------|---------|
| "This is a README file" | "Plugin providing 5 composable agent loop patterns for learning, red team review, triple-loop delegation, and parallel swarm execution" |
| "Contains a SKILL definition" | "Orchestrator skill that routes tasks to the correct loop pattern using a 4-question decision tree, manages shared closure sequence" |

## After Init

- Use [`rlm-distill-agent`](../rlm-distill-agent/SKILL.md) for ongoing cache updates
- Use [`rlm-curator`](../rlm-curator/SKILL.md) for querying, auditing, and cleanup
- Cache files should be `.gitignore`d if they contain project-specific summaries
