---
description: "Distill wiki source files into the RLM summary layer using the cheapest available LLM CLI. Routes to Copilot gpt-5-mini > Claude Haiku > Gemini Flash. Never uses Ollama."
argument-hint: "[--source <name>] [--engine copilot|claude|gemini] [--dry-run]"
allowed-tools: Bash, Read, Write
---

# /wiki-distill

Generates RLM summaries for all wiki nodes using cheap cloud LLM CLIs.

## Usage

```bash
# Auto-detect cheapest engine and distill all stale nodes
/wiki-distill

# Distill one source
/wiki-distill --source arch-docs

# Force a specific engine
/wiki-distill --engine claude
/wiki-distill --engine gemini
/wiki-distill --engine copilot

# Preview prompts without calling LLM
/wiki-distill --dry-run
```

## Engine Fallback Chain

```
1. copilot → gpt-5-mini        (cheapest, recommended)
2. claude  → claude-haiku-4-5  (fallback)
3. gemini  → gemini-3-flash-preview (final fallback)
```

`rlm-distill-ollama` is fully deprecated. Only cheap cloud models are used.

## Output

```
{wiki-root}/rlm/{concept}/
  summary.md   ← 1-5 sentence summary
  bullets.md   ← 6-10 key idea bullets
  deep.md      ← full multi-pass distillation
```

## Under the Hood

```bash
python ./scripts/distill_wiki.py --wiki-root {wiki_root} [options]
```

Calls `inject_summary.py` from the installed `rlm-factory` plugin
to persist each summary to the correct cache location.
