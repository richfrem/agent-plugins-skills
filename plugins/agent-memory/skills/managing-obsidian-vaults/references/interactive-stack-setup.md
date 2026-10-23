# Guided Super-RAG setup

This is a main-session skill workflow, including when the selected combination has
no wiki. Do not invoke a dedicated stack-setup agent or fork the conversation.

## Contents

- [Choose the stack](#choose-the-stack)
- [Carry the interview](#carry-the-interview)
- [Provision only selected layers](#provision-only-selected-layers)
- [Validate and report](#validate-and-report)

## Choose the stack

Inspect project state and availability of managing-rlm-cache, managing-vector-db
and managing-obsidian-vaults by name in the active runtime. Source files do not prove
installation. Respect an explicit combination; otherwise ask one question and mark
unavailable choices. Do not provision extra layers merely because they are installed.

| Choice | Required skill modes | Project files selected |
|---|---|---|
| RLM + vector, no wiki | RLM setup and vector setup | Ledger and vector profiles/manifests only |
| RLM + wiki | RLM setup and wiki setup B | Ledger plus wiki sources/output/config |
| Vector + wiki | Vector setup and wiki setup C | Vector plus wiki sources/output/config |
| Full Super-RAG | RLM, vector and wiki setup D | All three selected layers |
| One layer only | Its standalone setup | Only that layer's files |

For a missing required capability, explain it and let the user select an available
subset or authorized APM install. Preserve the chosen scope across the conversation.
Owning this reference does not select the wiki: RLM+vector must not create a wiki
root, source registry, wiki profiles, meta/config.yaml or meta/agent-memory.json.

## Carry the interview

Reuse known project root, namespace, layers, source roots, filters, destinations,
existing profile choices, model/storage settings and authorizations. Ask one missing
question per turn, with a recommended default. Do not restart the interview when
continuing another skill's mode. Keep the user's answers in the current conversation;
do not create an extra persistent setup state format.

Ask the project name/namespace once. Ask source scope once when layers share it;
let the user override different layer scopes explicitly. Validate paths before
traversal and confirm external scans. Never move raw files.

Preview proposed files/diffs before writes. Read-and-merge existing profiles,
source entries and metadata; preserve unknown fields. Resolve conflicting names
with a merge/rename/cancel choice. A prior authorization remains valid for the
agreed work; do not ask permission again for every already-approved step.

## Provision only selected layers

Continue these modes sequentially in the main conversation, carrying the answers:

1. If RLM is selected, use managing-rlm-cache guided setup. Configure project and
tools profiles/manifests, adding a wiki per-file profile only when wiki is selected.
Core lookup/injection are standard-library operations; only batch/service workflows
need their optional locked dependencies or selected model runner.
2. If vector is selected, use managing-vector-db guided setup. Preserve its selected
in-process/server mode, collection identities, manifest paths, chunk sizes, model
and device. Explain and perform dependency installation/model downloads only within
the authorized scope. RLM and vector can operate without a wiki.
3. If wiki is selected, use [guided wiki setup](interactive-setup.md) with the
already-chosen B/C/D combination (or A for wiki-only). Ask only wiki-specific gaps:
output root, source keys/labels and filters not previously supplied. Preserve the
nested raw-source schema and existing meta/agent-memory.json.

For full-stack model/data work, populate raw-file ledger summaries before vector
ingestion when enrichment is requested, then build wiki concepts and distill their
three concept layers. Do not claim vector ingestion is performed by wiki distillation.
For a no-wiki combination, stop after the selected ledger/vector work.

Preserve these separate interfaces:

| Interface | Shape / owner |
|---|---|
| rlm_profiles.json and flat include manifest | managing-rlm-cache, per-file summaries |
| vector_profiles.json and flat include manifest | managing-vector-db, collection/chunk configuration |
| rlm_wiki_raw_sources_manifest.json | managing-obsidian-vaults, nested sources objects |
| wiki-root/rlm or explicit concept cache | summary.md / bullets.md / deep.md per concept |

If a wiki config records a custom concept cache, pass the same --rlm-cache-dir to
build/distill/query as applicable. The bookkeeping YAML does not automatically set
script flags. For wiki+vector, explicitly resolve the vector skill's query.py and
set AGENT_MEMORY_VECTOR_QUERY; --vdb-profile only selects the configured profile.
Set AGENT_MEMORY_PROJECT_ROOT for each owning skill's scripts.

## Validate and report

Validate each selected layer independently. Inventory/query the RLM profile; check
vector config and, when authorized, ingest/query the intended collection; dry-run/
build/query/audit the wiki only if selected. A missing dependency, unavailable CLI
or skipped model run is deferred work, not a successful integration test.

Only if requested, provision the selected retrieval phases in the project's
authoritative instructions. Preserve existing bridges and unrelated text, and do
not advertise absent layers. Describe the chosen skills/modes instead of obsolete
agent names or command wrappers.

Finish with the exact combination, actual files/profiles and sources written,
storage/model settings, validation evidence, unconfigured layers and next named
skill modes. Do not print wiki next steps for a no-wiki combination. On a later
upgrade, read existing state and show an incremental plan; on cancel, stop pending
writes and report any already-applied changes.
