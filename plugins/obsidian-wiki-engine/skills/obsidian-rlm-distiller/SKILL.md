---
name: obsidian-rlm-distiller
plugin: obsidian-wiki-engine
description: "Distills wiki source files into the RLM summary layer (summary.md, bullets.md, deep.md) using the cheapest available LLM CLI. Routes to Copilot gpt-5-mini first, then Claude Haiku, then Gemini Flash. Never uses Ollama. Use when wiki nodes need RLM summaries generated or refreshed."
allowed-tools: Bash, Read, Write
---

## Dependencies

Requires Python 3.8+ and at least one CLI installed: `copilot`, `claude`, or `gemini`.

```bash
pip install -r requirements.txt
```

---
# Obsidian RLM Distiller

**Status:** Active
**Author:** Richard Fremmerlid
**Domain:** Obsidian Wiki Engine
**Replaces:** `rlm-distill-ollama` (fully deprecated)

## Purpose

Distills registered wiki source files into the three-layer RLM summary structure
inside `{wiki_root}/rlm/{concept}/`. Delegates work to the **cheapest available
LLM CLI** — never a local Ollama server.

## Cheap-Model Fallback Chain (Strict)

```
1. copilot CLI available?  → use gpt-5-mini        (fastest, free with Copilot Pro)
2. claude CLI available?   → use claude-haiku-4-5  (fallback)
3. gemini CLI available?   → use gemini-3-flash-preview (final fallback)
4. none found              → exit with instructions
```

> `rlm-distill-ollama` is fully deprecated. Only `rlm-distill-agent` pointing
> at cheap cloud models is supported.

## Output: Three-Layer RLM Structure

```
{wiki_root}/rlm/{concept}/
  summary.md    ← 1-5 sentence distilled summary
  bullets.md    ← key idea bullets (6-10 points)
  deep.md       ← full multi-pass distillation
```

## Usage

### Distill all stale wiki nodes
```bash
python ./scripts/distill_wiki.py --wiki-root /path/to/wiki-root
```

### Distill one named source
```bash
python ./scripts/distill_wiki.py --wiki-root /path/to/wiki-root --source arch-docs
```

### Force engine override
```bash
python ./scripts/distill_wiki.py --wiki-root /path/to/wiki-root --engine claude
python ./scripts/distill_wiki.py --wiki-root /path/to/wiki-root --engine gemini
python ./scripts/distill_wiki.py --wiki-root /path/to/wiki-root --engine copilot
```

### Use shared .agent/learning/ cache (colocates with rlm-factory)
```bash
python ./scripts/distill_wiki.py --wiki-root /path/to/wiki-root \
    --rlm-cache-dir /path/to/project/.agent/learning/rlm_wiki_cache
```

### Dry run
```bash
python ./scripts/distill_wiki.py --wiki-root /path/to/wiki-root --dry-run
```

## Engine Detection Logic

`distill_wiki.py` calls `shutil.which()` for each CLI in priority order.
The first one found and authenticated is used for the entire batch:

```python
ENGINE_PRIORITY = [
    ("copilot", "gpt-5-mini"),
    ("claude",  "claude-haiku-4-5"),
    ("gemini",  "gemini-3-flash-preview"),
]
```

## RLM Cache Storage

`distill_wiki.py` writes summaries directly into its own RLM cache directory.
No cross-plugin script calls are made (ADR-001 compliant).

Default cache: `{wiki-root}/rlm/{concept}/`

To colocate with rlm-factory under `.agent/learning/`, pass `--rlm-cache-dir`:
```bash
python ./scripts/distill_wiki.py --wiki-root /path/to/wiki-root \
    --rlm-cache-dir /path/to/project/.agent/learning/rlm_wiki_cache
```

The cache location is determined by configuration in `.agent/learning/rlm_profiles.json`
(the `cache` key of the wiki profile) — not by hard-coded cross-plugin paths.

## When to Use

- After `/wiki-ingest` populates new wiki nodes
- When RLM summaries are missing or stale
- Before running `/wiki-query` for optimal recall
- As part of the `/wiki-rebuild` full pipeline

## Related Scripts

- `distill_wiki.py` — cheap-model fallback orchestrator
- `raw_manifest.py` — `WikiSourceConfig` loader
- `audit.py` — identifies stale/missing RLM summaries
