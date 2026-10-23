# Acceptance Criteria: Managing RLM Cache

## Contract

- Resolve source files, profiles, manifests, caches, batch checkpoints and worker cwd from the consumer project, including an explicit AGENT_MEMORY_PROJECT_ROOT, without assuming the skill's install location.
- Lookup and summary injection work with the standard library and no vector/wiki sibling skill. Batch execution loads its own job and helper scripts; model-backed work uses the selected configured engine.
- Preserve the existing profile schema and file-summary ledger format. Audits and queries do not modify ledgers; injection uses the script rather than manual ledger edits.
- Show cleanup scope before applying deletions, and report actual affected paths and coverage.
- Batch discovery accepts relative/absolute paths inside the consumer root, rejects paths outside it and preserves source-relative cache keys. Helper commands handle spaces in skill/project/file paths.
- Delegate optional semantic search and wiki-layer distillation by installed skill name, without importing sibling implementations.

## Preserved Mode Criteria

- [Initialization](rlm-init-acceptance-criteria.md)
- [Search](rlm-search-acceptance-criteria.md)
- [Distillation](rlm-distill-agent-acceptance-criteria.md)
- [Curation](rlm-curator-acceptance-criteria.md)
- [Cleanup](rlm-cleanup-agent-acceptance-criteria.md)

## Evidence

Run model-resolution smoke tests without paid calls, profile inventory/query probes on temporary consumer data, and batch dry-run plus real cache-check/injection helper probes. Original routing cases and historical outcomes remain archived in evals/legacy; static preservation does not establish routing accuracy/F1.

## Main-session Interaction

- Setup and layer upgrades run directly in the current conversation, without a dedicated agent/command wrapper. Reuse supplied answers and ask at most one unresolved question per turn.
- Inspect existing state before proposing changes; preview/read-and-merge while preserving unknown fields and unrelated content. Continue only selected layers, skip completed setup phases and retain prior authorization.
- Missing installed capabilities, dependency/model execution and name conflicts are explicit decisions. Cancel stops pending writes and reports any earlier applied work.
- Explicit operational requests use their existing modes without restarting setup; do not claim model-measured routing or conversation quality from static scenarios.

Interactive routing additions and task-success scenarios are verifier-authored supplements in evals; the original archived 192 routing cases/outcomes remain intact.
