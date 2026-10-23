---
name: managing-rlm-cache
plugin: agent-memory
description: >
  Interactive RLM setup wizard and summary-ledger maintenance in the main conversation.
  Initialize, search, distill, curate, audit and clean RLM summary ledgers.
  Use for RLM profiles, summary injection, keyword cache lookup, missing summaries,
  stale entries and batch distillation. Wiki concept summaries use managing-obsidian-vaults.
allowed-tools: Bash, Read, Write
---

# Managing RLM Cache

Read the matching workflow before acting. Run commands from this skill's folder;
set `AGENT_MEMORY_PROJECT_ROOT` to the consumer project, including for global installs.

## Contents

[Interaction](#interaction) · [Constraints](#constraints) · [Workflow](#workflow) · [Quick start](#quick-start) · [Verification](#verification)

## Interaction

Treat slash-invocation arguments as supplied requirements; do not ask for them again.

For setup, semantic-cache onboarding or layer upgrades, read [guided setup](references/interactive-setup.md).
Conduct it here in the main conversation; reuse known answers and ask one unresolved question per turn.
Offer available standalone/combined choices, preview the config changes, then apply the authorized scope.
Continue other skills' selected modes in the same session; preserve answers and never launch a setup agent.
For an explicit query/audit request, use the matching mode directly without restarting an interview.

## Constraints

- Read each source fully before summarizing. Report source paths and injected summaries.
- Never edit ledger files manually: use `scripts/inject_summary.py` or `scripts/swarm_run.py`.
- Audit and query are read-only. Show cleanup dry runs and confirm scope before applying deletions.
- Use configured profiles in the consumer's `.agent/learning/rlm_profiles.json`.
- Search summaries first, then delegate semantic retrieval to managing-vector-db if installed,
  then use scoped exact search. Do not import another skill's Python implementation.
- Ledger lookup/injection require only Python's standard library. Batch jobs use PyYAML;
  model-backed distillation additionally needs the selected CLI or configured service.

## Workflow

| Request | Read first |
|---|---|
| Initialize, add profile or choose stack | [Guided setup](references/interactive-setup.md), [initialization](references/rlm-init.md), [bootstrap guide](references/rlm-bootstrap-guide.md) |
| Keyword lookup / three-phase search | [Search](references/rlm-search.md) |
| Read sources and inject summaries | [Distillation](references/rlm-distill-agent.md) |
| Maintain coverage / batch work | [Curation](references/rlm-curator.md) |
| Compare manifest with cache | [Audit](references/rlm-audit.md) |
| Preview and prune stale entries | [Cleanup](references/rlm-cleanup-agent.md) |
| Wiki summary, bullets and deep layers | Use managing-obsidian-vaults, wiki distillation mode; verify it is installed |

## Quick start

```bash
python3 scripts/inventory.py --profile project
python3 scripts/query_cache.py "session memory" --profile project
python3 scripts/inject_summary.py --profile project --file path/to/file.py --summary "Dense summary."
python3 scripts/cleanup_cache.py --profile project
```

For jobs, use [the job template](assets/jobs/distill_wiki.job.md) and the
[model catalog](references/cheapest_models.md). Preserve the selected engine and profile.

## Verification

Rerun inventory/query on the chosen profile and report actual coverage and errors.
Smoke-test engine resolution without model calls: `python3 scripts/distill_one.py --mock`.
Read [distillation criteria](references/rlm-distill-agent-acceptance-criteria.md),
[curation recovery](references/rlm-curator-fallback-tree.md) and
[ledger architecture](references/RLM_ARCHITECTURE.md) when applicable.

[rlm-cleanup-agent criteria](references/rlm-cleanup-agent-acceptance-criteria.md) · [rlm-curator criteria](references/rlm-curator-acceptance-criteria.md) · [rlm-init criteria](references/rlm-init-acceptance-criteria.md) · [rlm-search criteria](references/rlm-search-acceptance-criteria.md)

Follow the [acceptance contract](references/acceptance-criteria.md); browse the [resource index](references/resource-index.md). Supplemental: [BLUEPRINT](references/BLUEPRINT.md) · [gap analysis rlm v1](references/gap_analysis_rlm_v1.md) · [prompt](references/prompt.md) · [research-summary](references/research-summary.md) · [summary](references/research/summary.md) · [distill wiki.job](references/../assets/jobs/distill_wiki.job.md) · [rlm summarize general](references/../assets/templates/prompts/rlm/rlm_summarize_general.md) · [rlm summarize tool](references/../assets/templates/prompts/rlm/rlm_summarize_tool.md). [Research architecture](references/research/../BLUEPRINT.md).
