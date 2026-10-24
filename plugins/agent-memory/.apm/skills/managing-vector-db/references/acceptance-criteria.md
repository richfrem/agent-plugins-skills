# Acceptance Criteria: Managing Vector DB

## Contract

- Resolve project manifests, profiles and data from the consumer project, including explicit AGENT_MEMORY_PROJECT_ROOT; resolve dependency files and executable helpers from this skill.
- Preserve existing vector profile/manifest schemas, collection identities, embedding/chunking parameters and configured consumer data paths.
- Operate independently of RLM and Obsidian skill implementations. Optional RLM enrichment reads consumer-owned summary data, without importing another skill.
- Select the intended profile for ingestion, query, audit and cleanup. Report the scope, affected sources/chunks, retrieval results and failures.
- Use the supported collection API/scripts; never inspect or mutate backing SQLite/Parquet files directly. Coverage audits do not mutate index records.
- Prefer in-process persistence; a server starts only when needed, binds to localhost and is checked before duplicate launch.
- Keep vector dependencies optional for the other skills. Dependency installation, database writes and model downloads require the selected workflow's authorization.

## Preserved Mode Criteria

- [Initialization](vector-db-init-acceptance-criteria.md)
- [Search and database sovereignty](vector-db-search-acceptance-criteria.md)
- [Server lifecycle](vector-db-launch-acceptance-criteria.md)

The consumer's .agent/learning/vector_profiles.json remains the operational profile location; historical asset-path wording in the detailed initialization criterion does not relocate consumer data into the installed skill.

## Evidence

Check profile/manifest resolution from an isolated skill copy and temporary consumer root before any live integration run. Query recently ingested sources in the selected collection when live database/model execution is authorized. Offline configuration probes alone do not certify ChromaDB or embedding integration.

## Main-session Interaction

- Setup and layer upgrades run directly in the current conversation, without a dedicated agent/command wrapper. Reuse supplied answers and ask at most one unresolved question per turn.
- Inspect existing state before proposing changes; preview/read-and-merge while preserving unknown fields and unrelated content. Continue only selected layers, skip completed setup phases and retain prior authorization.
- Missing installed capabilities, dependency/model execution and name conflicts are explicit decisions. Cancel stops pending writes and reports any earlier applied work.
- Explicit operational requests use their existing modes without restarting setup; do not claim model-measured routing or conversation quality from static scenarios.

Interactive routing additions and task-success scenarios are verifier-authored supplements in evals; the original archived 192 routing cases/outcomes remain intact.
