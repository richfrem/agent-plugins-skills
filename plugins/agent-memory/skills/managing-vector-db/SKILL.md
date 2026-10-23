---
name: managing-vector-db
plugin: agent-memory
description: >
  Interactive ChromaDB setup wizard and vector-index operations in the main conversation.
  Configure profiles, ingest files,
  search semantically, audit coverage, clean orphaned chunks and launch a local
  server. Use for vector database maintenance and phase-two semantic retrieval.
allowed-tools: Bash, Read, Write
---

# Managing Vector DB

Read the matching workflow. Run commands from this skill's folder with
`AGENT_MEMORY_PROJECT_ROOT` set to the consumer project for global installations.

## Contents

[Interaction](#interaction) · [Constraints](#constraints) · [Workflow](#workflow) · [Quick start](#quick-start) · [Verification](#verification)

## Interaction

Treat slash-invocation arguments as supplied requirements; do not ask for them again.

For setup or layer upgrades, read [guided setup](references/interactive-setup.md) before configuring anything.
Stay in the main conversation, reuse supplied answers and ask one unresolved question per turn.
Recommend standalone/in-process defaults; confirm only missing scope and conflicting or destructive changes.
Preview merged profiles and dependency needs, then perform the authorized work and validate actual results.
Continue selected sibling-skill modes in this session; never fork a setup agent or repeat the interview.
For an explicit ingest/query/audit request, use its mode directly.

## Constraints

- Always select the intended profile; preserve existing manifests and collection settings.
- Default to in-process storage. Use server mode only for concurrent writers.
- Bind servers to `127.0.0.1`; never expose the service on public interfaces.
- Access collections through the scripts/API, never edit SQLite or Parquet backing files.
- Audits are read-only. Preview cleanup and confirm deletion scope before applying changes.
- Report profile, affected files/chunks, failures and retrieval evidence.
- Install this skill's locked dependencies only when requested. RLM and wiki skills are optional.

## Workflow

| Request | Read first |
|---|---|
| Configure profiles / dependencies | [Guided setup](references/interactive-setup.md), [initialize](references/vector-db-init.md), [bootstrap guide](references/vector-db-bootstrap-guide.md) |
| Index new/changed sources or rebuild | [Ingest](references/vector-db-ingest.md) |
| Retrieve related concepts/chunks | [Search](references/vector-db-search.md) |
| Compare manifest and indexed coverage | [Audit](references/vector-db-audit.md) |
| Remove orphaned chunks | [Cleanup](references/vector-db-cleanup.md) |
| Launch/inspect localhost service | [Server lifecycle](references/vector-db-launch.md) |

## Quick start

```bash
python3 scripts/init.py
python3 scripts/ingest.py --profile wiki --since 24
python3 scripts/query.py "how does session memory persist" --profile wiki --limit 5
python3 scripts/audit_vector.py --profile wiki
```

Use existing `.agent/learning/vector_profiles.json` and configured manifests.
RLM enrichment reads consumer cache data without importing another skill.
For source discovery, use managing-rlm-cache first if it is installed and configured.

## Verification

Confirm ingested files are retrievable in the intended collection and rerun coverage.
Read [retrieval criteria](references/vector-db-search-acceptance-criteria.md) and
[recovery](references/vector-db-search-fallback-tree.md) before diagnosing missing results.

[vector-db-init criteria](references/vector-db-init-acceptance-criteria.md) · [vector-db-launch criteria](references/vector-db-launch-acceptance-criteria.md)

Follow the [acceptance contract](references/acceptance-criteria.md); browse the [resource index](references/resource-index.md). Supplemental: [rag design choices](references/rag_design_choices.md) · [README](references/stabilizers/README.md) · [vector consistency check](references/stabilizers/vector_consistency_check.md). [Dependency setup](references/dependencies.md).
