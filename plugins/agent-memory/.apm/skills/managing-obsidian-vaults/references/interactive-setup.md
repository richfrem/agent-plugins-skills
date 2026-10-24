# Guided vault and wiki setup

Run in the main conversation, without a setup agent or context fork. Carry forward
known answers and current authorization. For vault settings alone, use initialization
mode; do not force a wiki, RLM ledger or vector database on a note/Canvas operation.

## Contents

- [Choose layers](#choose-layers)
- [Discover sources](#discover-sources)
- [Preview and merge](#preview-and-merge)
- [Configure integrations](#configure-integrations)
- [Execute and validate](#execute-and-validate)
- [Resume](#resume)

## Choose layers

Inspect existing wiki-root/meta/config.yaml and project learning profiles first.
Check optional skills by runtime name. Reuse an explicit user choice; otherwise ask
one question with available choices and recommend the smallest sufficient scope.

| Mode | Selected layers | Required capabilities |
|---|---|---|
| A: Wiki only (default) | Vault/wiki build, query, audit and optional wiki distillation/lint | This skill; dependencies and CLI only for operations that need them |
| B: Wiki + file-summary ledger | Wiki and raw-source RLM summaries | managing-rlm-cache |
| C: Wiki + semantic retrieval | Wiki and vector index | managing-vector-db |
| D: Full Super-RAG | Wiki, per-file ledger and vector retrieval | Both sibling skills |

Wiki concept summary.md/bullets.md/deep.md generation belongs to this skill and does
not require the RLM sibling. The optional ledger is a separate one-summary-per-file
store. Do not advertise standalone semantic lint/distillation as dependency-free:
they need the chosen cloud CLI. Never use a local-model fallback silently.

If a selected sibling is missing, explain the dependency and offer an available
subset or an APM installation within authorized scope. Do not silently change modes.
For combinations with no wiki, use [the stack setup](interactive-stack-setup.md).

## Discover sources

Ask one unresolved question per turn. Infer answers from the request and existing
configuration rather than asking them again:

1. Consumer root and namespace/project name.
2. Wiki output root (suggest the consumer's .wiki); resolve relative paths against
   the consumer, and include new-directory creation in the proposed changes.
3. Content source roots: inspect candidate project directories and show a numbered
   table with descriptions. Accept numbered selections, custom paths or both.
4. A stable source name and human-readable label for each chosen root.
5. Included extensions (suggest .md, .ts, .py where relevant), then extra exclusions.

Keep discovery within authorized roots. Confirm external directory scans before
traversing them. Validate selected paths; ask to correct or skip a missing one.
Never move or rename raw content. Exclude generated output, .git, dependencies,
worktrees, caches and temporary traces. Preserve user-selected patterns and apply
chosen extensions to every relevant source entry.

## Preview and merge

Show the complete manifest/diff and directory plan before writing. Use the nested
schema below for .agent/learning/rlm_wiki_raw_sources_manifest.json:

```json
{
  "namespace": "project-name",
  "wiki_root": "/absolute/path/to/.wiki",
  "global_excludes": [".git/", "node_modules/", ".venv/", "__pycache__/"],
  "sources": {
    "architecture": {
      "path": "docs/architecture",
      "label": "Architecture",
      "extensions": [".md", ".ts", ".py"]
    }
  }
}
```

Read an existing registry before changes. Merge source objects by key; there is no
flat include array in this schema. Retain unknown fields, existing labels and filters.
If keys conflict, present a diff and ask to merge, rename or cancel. Overwrite/removal
requires the user's explicit scope. Apply the reviewed, authorized changes.

Create wiki/ and meta/ inside the selected wiki output root. Create rlm/ only when
using that local concept-summary destination. Preserve existing meta/agent-memory.json;
initialize it to an empty object only when absent. Never erase its hashes/mappings
while adding a source or layer.

Read-and-merge meta/config.yaml, retaining its existing keys. Record namespace,
wiki_root, chosen setup_mode (A/B/C/D) and configured engine. Set vdb_profile only
for C/D. Record the concept rlm_cache_dir only if configured, otherwise the scripts
use wiki-root/rlm. Set created_at only for a new config, not on every resume.

## Configure integrations

For B/D, continue managing-rlm-cache setup inline with the same namespace, source
choices and selected scope. Its optional wiki ledger profile uses its own flat
rlm_wiki_manifest.json and per-file cache; do not point it at the nested raw-source
registry above. Preserve existing profiles and their keys.

For C/D, continue managing-vector-db setup inline. The wiki profile needs its own
flat vector_wiki_manifest.json, distinct collections and an explicit manifest field.
Preserve selected chunking, model/device and storage mode. Empty chroma_host selects
in-process operation; localhost selects a server. Resolve that skill's query.py and
set AGENT_MEMORY_VECTOR_QUERY for integrated wiki semantic lookup.

Configuration bookkeeping is not automatic CLI configuration. Pass the selected
wiki root, profile and any non-default concept --rlm-cache-dir to the scripts that
need them. Do not point wiki concept queries at the per-file ledger directory.

## Execute and validate

Set AGENT_MEMORY_PROJECT_ROOT to the consumer root. Only run the chosen operations:

1. Validate-only vault settings before initializing the vault. Use this skill's
   locked dependencies if required and authorized; do not install arbitrary packages.
2. In B/D, distill selected raw sources into the RLM ledger if that work is authorized;
   report its inventory coverage. In C/D, run vector ingestion after ledger population
   when enrichment is selected, then verify retrieval from the chosen profile.
3. Run wiki build dry-run, then build concept nodes from the registered sources.
   Wiki-only mode starts here; it has no RLM/vector prerequisite. Existing concept
   summaries can enrich build output; initial concept distillation follows first build.
4. If requested, distill concept layers with this skill's configured cloud engine.
   Query at summary level first, expand only as needed, and run a structural audit.
   Semantic lint writes a report and never autonomously edits concept pages.

Every cross-skill phase remains in this conversation. Resolve each script from its
owning skill folder, keeping the shared consumer root and answers. Do not launch
an agent, duplicate source files or repeat completed interviews.

If retrieval guidance is requested, modify only the project's authoritative
instructions, preserving thin bridges and unrelated content. Describe only installed,
configured retrieval layers; never advertise an index before it exists.

## Resume

For a later source/layer addition, read the current state and show just the incremental
diff. On cancel, stop the pending change and report prior writes already applied.
Finish with selected mode, actual files/sources, validation results, deferred work and
next skill modes. Keep per-file ledger and per-concept summary readiness separate.
