# Guided vector search setup

Conduct this wizard in the main conversation. Do not launch an agent or fork the
interview. Carry supplied answers and approvals across skill transitions. Explicit
query/ingest/audit requests use their existing mode without a new setup interview.

## Contents

- [Scope](#scope)
- [Dependencies and storage](#dependencies-and-storage)
- [Interview and profiles](#interview-and-profiles)
- [Apply and verify](#apply-and-verify)
- [Continue or resume](#continue-or-resume)

## Scope

Inspect consumer .agent/learning/vector_profiles.json and existing manifests.
Check optional skills by name in the runtime. Ask one unresolved question per turn.
If the user already chose a combination, retain it rather than asking again.

| Choice | Result | Optional skill needed |
|---|---|---|
| A: Standalone (default) | General knowledge index | None |
| B: Vector + RLM | Index enriched by existing per-file summaries | managing-rlm-cache |
| C: Vector + wiki | General/wiki retrieval profiles | managing-obsidian-vaults |
| D: Full Super-RAG | General/wiki profiles plus ledger enrichment | Both |

Mark unavailable combinations. Offer an available subset or explain the APM install
needed for a selected missing skill. Never silently add or drop a layer. Wiki profiles
are created only when the selected scope includes the wiki.

## Dependencies and storage

Check imports for chromadb, sentence_transformers and the locked LangChain
integrations. If dependencies are unavailable, explain what needs installing and
use this skill's requirements.txt only within the authorized scope. Do not issue
ad-hoc package lists. Explain embedding model downloads before initial ingestion.

Default to in-process persistence. Ask about server mode only if concurrency is
required or storage mode is genuinely unresolved. A localhost server is needed for
concurrent processes; never bind it to a public interface. Preserve an existing
valid connection configuration unless changing it is part of the request.

The executable selects its client from chroma_host: use an empty string for
in-process mode and 127.0.0.1 for server mode. An inprocess_mode flag alone does not
select the implementation. Keep an existing flag consistent if it is present.

## Interview and profiles

Ask only for missing inputs, one at a time:

1. Consumer project root, namespace and target profile names.
2. Content roots and include/exclude patterns; inspect suggested directories first.
3. Content type: Markdown/wiki, code, or large documents.
4. Storage location and embedding model/device if not already configured.
5. Additional custom profiles, if the requested scope leaves this open.

Suggested parent/child chunk sizes are 1200/400 for Markdown, 2000/400 for code,
and 3000/500 for large documents. Preserve user/configured values and use sensible
overlap (for example 20% parent and 50 child), not an unannounced reset.

Each profile must include a manifest path; the loader rejects one without it:

```json
{
  "default_profile": "knowledge",
  "profiles": {
    "knowledge": {
      "description": "Project semantic index",
      "manifest": ".agent/learning/vector_knowledge_manifest.json",
      "child_collection": "knowledge_children",
      "parent_collection": "knowledge_parents",
      "embedding_model": "nomic-ai/nomic-embed-text-v1.5",
      "chroma_host": "",
      "chroma_port": 8110,
      "chroma_data_path": ".vector_data",
      "batch_size": 1000,
      "parent_chunk_size": 2000,
      "parent_chunk_overlap": 200,
      "child_chunk_size": 400,
      "child_chunk_overlap": 50,
      "device": "cpu"
    }
  }
}
```

Use the selected content/chunking/connection values, not blindly this example.
For C/D add a wiki profile with distinct wiki_children/wiki_parents collections and
its own vector_wiki_manifest.json. Its include paths come from the chosen raw wiki
sources when raw-to-concept reverse mapping is wanted. Never reuse the nested wiki
raw-source registry as a flat vector manifest. The manifest shape is:

```json
{
  "include": ["docs/", "README.md"],
  "exclude": ["node_modules", "__pycache__", ".git", "*.pyc", ".vector_data"],
  "extensions": [".md", ".py"],
  "recursive": true
}
```

Read-and-merge existing files, retaining unknown keys and unaffected profiles. Show
proposed contents/diffs. For a name/collection conflict, ask to merge, rename or cancel;
never offer destructive overwrite as the default. Apply writes within the authorized
scope after resolving conflicts. Do not run scripts/init.py over chosen profiles:
its generic defaults must not overwrite the connection settings from this interview.

## Apply and verify

Set AGENT_MEMORY_PROJECT_ROOT to the consumer root, and run this skill's scripts
from its folder. Validate profile/manifest JSON and that included paths exist.
Preview the configured manifests and matched source scope without indexing first.
The ingest CLI has no --dry-run option. When dependencies and the requested model/
database writes are authorized, run the supported full/incremental ingestion and
test retrieval from the same collection afterward. Confirm flags against script
help. Preserve collection identity and report failures.

For B/D, populate selected RLM source summaries first if the user requested enrichment;
ingest then reads the consumer-owned cache without importing a sibling skill.
For C/D, carry the selected profile/root into managing-obsidian-vaults setup inline.
For integrated wiki semantic lookup, resolve this skill's scripts/query.py and set
AGENT_MEMORY_VECTOR_QUERY explicitly. --vdb-profile chooses a profile, not a script.

## Continue or resume

Retain the shared conversation's root, scope, content choices and answers while
continuing a selected sibling mode. Never dispatch a setup agent or restart the
combination interview. A later layer addition changes only its necessary profiles.

If retrieval guidance is requested, update the project's authoritative instructions
for installed/configured layers only; preserve existing bridges and other content.
Finish with actual files/profiles, storage mode, validation evidence and next ingest/
search/server steps. If dependencies or a model run are deferred, report setup-only
readiness. On cancel, stop pending writes and describe earlier applied changes.
