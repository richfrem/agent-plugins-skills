# Obsidian Wiki Distillation Guide

## Contents
- [Cheap Model Fallback Hierarchy](#cheap-model-fallback-hierarchy)
- [Three-Layer RLM Output Structure](#three-layer-rlm-output-structure)
- [Engine Detection & CLI Overrides](#engine-detection--cli-overrides)
- [RLM Cache Storage & Colocation](#rlm-cache-storage--colocation)

---

## Cheap Model Fallback Hierarchy

The distiller delegates distillation to cheap cloud LLMs, never local servers:

1. **GitHub Copilot CLI:** `gpt-5-mini` (primary, fast, credit-based)
2. **Claude CLI:** `claude-haiku-4-5` (first fallback)
3. **Antigravity CLI (`agy`) / Gemini CLI:** `gemini-3-flash-preview` (secondary fallback)
4. **None found:** Exits with diagnostic remediation steps

---

## Three-Layer RLM Output Structure

For each processed concept slug, distillation generates:

```
{wiki_root}/rlm/{concept}/
  summary.md    <- 1-5 sentence distilled summary
  bullets.md    <- 6-10 structural key idea bullets
  deep.md       <- Full multi-pass distillation
```

---

## Engine Detection & CLI Overrides

Detection tests availability and authorization via `shutil.which()`:

```bash
# Run distillation with auto-detected engine
python ./scripts/distill_wiki.py --wiki-root <path>

# Force specific CLI backend
python ./scripts/distill_wiki.py --wiki-root <path> --engine copilot
python ./scripts/distill_wiki.py --wiki-root <path> --engine claude
python ./scripts/distill_wiki.py --wiki-root <path> --engine agy
```

---

## RLM Cache Storage & Colocation

By default, RLM nodes land in `{wiki_root}/rlm/{concept}/`.
To colocate with system-wide caches:
```bash
python ./scripts/distill_wiki.py --wiki-root <path> \
    --rlm-cache-dir .agent/learning/rlm_wiki_cache
```
