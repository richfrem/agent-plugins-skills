---
name: update-cli-models
plugin: cli-agents
description: >
  Updates model catalogs and cheapest-model references for all CLI backends
  (copilot, agy, claude, codex, llama). Researches current model IDs and
  pricing from official sources, updates the per-CLI JSON files, refreshes
  cheapest_models.json/md if the cheapest pick changed, then propagates all
  copies via sync_cheapest_models.py. Trigger with "update cli models",
  "refresh model prices", "model costs are stale", "sync model catalog",
  or "update copilot/agy/claude model list".
argument-hint: "[cli-name or 'all']"
allowed-tools: Bash, Read, Write
---

# update-cli-models: Model Catalog Update Protocol

When triggered, **execute all steps below in order**. This is an active update
run — not a reference. Fetch live data, diff against current JSON files,
write changes, and sync at the end.

---

## Reference Files (master copies — only these are ever edited directly)

| File | CLI | Key field |
|---|---|---|
| `plugins/cli-agents/references/copilot-models.json` | `copilot` | `cli_id` uses **dot** notation e.g. `claude-sonnet-4.6` |
| `plugins/cli-agents/references/agy-models.json` | `agy` | Gemini models with thinking levels |
| `plugins/cli-agents/references/claude-models.json` | `claude` | `cli_id` uses **dash** notation e.g. `claude-sonnet-5` — more models than Copilot |
| `plugins/cli-agents/references/codex-models.json` | `codex` | OpenAI models via codex CLI |
| `plugins/cli-agents/references/cheapest_models.json` | all | **Master** cheapest pick per backend |
| `plugins/cli-agents/references/cheapest_models.md` | all | **Master** human-readable cheapest + Copilot tier table |

> Copies under individual skills are **never edited directly** — the sync script handles them.

---

## Step 1 — Fetch current data from official sources

Fetch each source using `read_url_content`. Use the markdown API endpoints
where available — do NOT scrape raw HTML.

| CLI | Fetch URL |
|---|---|
| `copilot` pricing | `https://docs.github.com/api/article/body?pathname=/en/copilot/reference/copilot-billing/models-and-pricing` |
| `copilot` model IDs | `https://docs.github.com/api/article/body?pathname=/en/copilot/reference/ai-models/supported-models` |
| `agy` (Gemini) | `https://ai.google.dev/pricing` |
| `claude` | `https://platform.claude.com/docs/en/about-claude/models/overview` |
| `codex` (OpenAI) | Try `https://openai.com/api/pricing/` — if 403, use `search_web` for "OpenAI API pricing [current year] per million tokens" |

For each source extract:
- Exact CLI identifier (not display name)
- Input / output price per 1M tokens
- Cached input price
- Cache write cost (Anthropic only)
- Context window (if available)
- Long context pricing tiers and thresholds
- Status: GA / preview / withdrawn / deprecated

---

## Step 2 — Diff against current JSON and update

For each CLI backend, compare fetched data to the current JSON:

**New model?** → Add full entry to `models[]` array, add to appropriate `cost_tiers` bucket.

**Price changed?** → Update `pricing_usd_per_1m` and `credits_per_1m` fields.

**Model withdrawn/deprecated?** → Set `"status": "withdrawn"` or `"status": "deprecated"`, `"available": false`. Do NOT delete the entry.

**Long context tier missing?** → Add `long_context_pricing_usd_per_1m` field with `threshold_note`.

**After any changes**, update `_meta.updated` to today's date on that JSON file.

### CLI-specific rules

- **copilot**: Claude IDs use **dots** (`claude-sonnet-4.6`). Prices in AI Credits (`credits_per_1m`). See `_meta.credits_formula`.
- **claude**: Claude IDs use **dashes** (`claude-sonnet-5`). Has more models than Copilot — the files intentionally differ.
- **agy**: Each thinking level (Low/Med/High) is a separate `cli_id` entry. Do not collapse them.
- **codex**: OpenAI models only. Matches OpenAI API pricing (not Copilot AI Credits).

---

## Step 3 — Check if cheapest pick has changed

Compare current `cheapest_models.json` entries against what Step 1 found:

| CLI | Current cheapest | Verification question |
|---|---|---|
| `copilot` | `gpt-5.4-nano` (20 cr/1M input) | Is there anything cheaper in the catalog? |
| `agy` | `gemini-3.5-flash` (Low) | Is Flash (Low) still the cheapest Gemini? |
| `claude` | `claude-haiku-4-5` ($1/1M input) | Is Haiku still cheapest current Claude? |
| `codex` | `gpt-5-mini` ($0.25/1M input) | Is there anything cheaper? |
| `llama` | `gemma-4-12b` (free, self-hosted) | Always free — no change expected |

If cheapest changed for any CLI:
1. Edit `plugins/cli-agents/references/cheapest_models.json` — update `model` and `description`
2. Edit `plugins/cli-agents/references/cheapest_models.md` — update main table row; if Copilot changed, update the Copilot tiers table too

---

## Step 4 — Run sync script

After ALL JSON updates are done, run:

```bash
python3 plugins/cli-agents/scripts/sync_cheapest_models.py
```

Verify output shows `updated: N files` with no errors. This propagates the
master `cheapest_models.json` and `.md` to all copies across the repo.

---

## Step 5 — Report

Summarise what changed:

```
✅ update-cli-models complete — [DATE]

Updated JSON files:
  - copilot-models.json: [N new models, M price changes]
  - agy-models.json: [changes or "no changes"]
  - claude-models.json: [changes or "no changes"]
  - codex-models.json: [changes or "no changes"]

Cheapest model changes:
  - [cli]: [old model] → [new model]  (or "no changes")

Sync: [N] copies of cheapest_models updated across repo.
```

---

## Common Failures

- **Display name vs CLI ID**: Copilot shows "GPT-5.4 nano" — CLI arg is `gpt-5.4-nano`. Always use CLI identifier.
- **Dot vs dash notation**: `claude-sonnet-4.6` (Copilot) ≠ `claude-sonnet-4-6` (direct API). Wrong notation silently fails at runtime.
- **agy thinking levels**: `gemini-3.5-flash` (medium) ≠ `gemini-3.5-flash-low`. Separate `cli_id` entries.
- **Long context pricing**: Always capture both tiers when a model has them.
- **OpenAI 403**: `openai.com/api/pricing/` blocks fetchers. Use `search_web` fallback.
- **Symlinks**: Some copies of `cheapest_models.json` are symlinks — `sync_cheapest_models.py` skips them automatically.
- **Do not delete entries**: Mark withdrawn models with `"available": false`, `"status": "withdrawn"`. Deletion breaks history.
