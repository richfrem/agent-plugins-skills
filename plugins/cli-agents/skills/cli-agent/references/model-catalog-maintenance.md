# Model catalog maintenance

## Contents

- [Ownership and schema](#ownership-and-schema)
- [Official sources](#official-sources)
- [Update and verification](#update-and-verification)

## Ownership and schema

In the caller-selected source repository, the owning plugin's `references/`
contains the canonical catalogs. Locate the cli-agents plugin there before editing.
Bundled `references/copilot-models.json`, `references/agy-models.json`,
`references/claude-models.json` and `references/codex-models.json` are installed
readable copies; modify their canonical owners when maintaining the source repository.
`references/cheapest_models.json` and `references/cheapest_models.md` contain default picks.
Do not mutate installed copies as competing source authorities.

Retain `_meta.schema_version: 2`, runtime_id/provider/availability,
`native_capabilities` for planning/worktree/subagents (native/portable/unknown),
and supported `effort_modes`. Capability tiers low/medium/high reference existing
available model IDs. They select model candidates, not universal reasoning settings.
Each model retains context_window_k, max_output_k, pricing_usd_per_1m and tool_support;
unknown limits/pricing stay null or explicitly unknown. Preserve unknown schema fields.
Explicit model choices override tier defaults; withdrawn entries remain historical.

## Official sources

Use available browsing tools, preferring provider Markdown/API documentation.
Verify runtime identifiers with the selected provider's supported model list;
display names, hosted aliases and direct API IDs need not be interchangeable.

| Provider | Sources |
|---|---|
| Copilot | [Models](https://docs.github.com/en/copilot/reference/ai-models/supported-models), [billing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing) |
| Agy/Gemini | `agy models` for hosted IDs; [Gemini pricing](https://ai.google.dev/pricing) for official API prices |
| Claude | [Models](https://platform.claude.com/docs/en/models/overview), [pricing](https://platform.claude.com/docs/en/about-claude/pricing), [CLI configuration](https://code.claude.com/docs/en/model-config) |
| Codex/OpenAI | [Models](https://developers.openai.com/api/docs/models), [pricing](https://openai.com/api/pricing/); installed CLI model availability |
| Local runtime | Configured server's model inventory and measured limits |

Capture exact IDs, status, input/output/cached-input costs, cache-write costs where
applicable, context/output limits and long-context thresholds. Copilot credit rates
are not direct API dollar prices. Agy aliases require separate hosted verification.
If a source is unavailable, use another official source or record the gap; do not
infer withdrawal merely because an account's picker omits a model.

## Update and verification

Add verified models with complete schema fields. Update prices with evidence;
mark confirmed deprecated/withdrawn entries without deleting them. Reconcile
cost_tiers, capability_tiers and strategy only for verified supported candidates.
Update the catalog's verification date and source URLs after a successful refresh.

Compare available models on the applicable pricing basis before changing cheapest
picks. Preserve the current pick when data is insufficient, and report why.
Synchronize only within the explicit caller-supplied repository; preview destinations
first. Managed symlinks retain canonical ownership; installed copies are refreshed
through the installer rather than treated as source files.

Use `scripts/model_catalog.py`'s load_catalog/validate_catalog interfaces to check
schema and tier integrity. Run task-appropriate router regression checks in the
source repository and verify any changed model's runtime availability only when
that probe is authorized. Report exact sources, model/price changes, cheapest-pick
changes or no change, synchronized copy counts and unresolved coverage.
