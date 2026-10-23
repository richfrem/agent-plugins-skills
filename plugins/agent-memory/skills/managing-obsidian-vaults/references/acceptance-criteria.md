# Acceptance Criteria: Managing Obsidian Vaults

## Contract

- Resolve vault/wiki roots explicitly and consumer learning profiles through AGENT_MEMORY_PROJECT_ROOT or caller-project discovery. Scripts, templates and parser helpers remain skill-local and portable.
- A wiki-only install builds, queries and audits without RLM/vector sibling implementations. Distillation and semantic lint share this skill's configured cloud-engine implementation; no silent local-model fallback.
- Preserve raw source content and existing config/frontmatter. Merge multiple source records for one concept; retain wiki manifest/meta schemas and separate summary.md, bullets.md and deep.md outputs.
- Queries start with summary disclosure and expand on demand. Structural/semantic reports do not autonomously rewrite concept nodes.
- Retain safe note/Base/Canvas operations, syntax parsing, link/embed distinction and read-only graph traversal under the detailed criteria below.
- Combined setup delegates each phase to its owning installed skill, preserves chosen layers and existing profiles, and sets AGENT_MEMORY_VECTOR_QUERY explicitly for optional semantic lookup. --vdb-profile selects a profile, not an executable.

## Preserved Mode Criteria

- [Vault initialization](obsidian-init-acceptance-criteria.md)
- [Markdown syntax](obsidian-markdown-mastery-acceptance-criteria.md)
- [Note operations](obsidian-vault-crud-acceptance-criteria.md)
- [Bases](obsidian-bases-manager-acceptance-criteria.md)
- [Canvas](obsidian-canvas-architect-acceptance-criteria.md)
- [Graph traversal](obsidian-graph-traversal-acceptance-criteria.md)

## Evidence

Use isolated temporary consumer vault/wiki data for init validation, build/query/audit probes and parser tests. Run distillation/lint dry runs without calling a model when possible. Original wiki/vault routing cases remain archived; runtime routing precision and semantic-model quality require measured campaigns and cannot be inferred from structural passes.

## Main-session Interaction

- Setup and layer upgrades run directly in the current conversation, without a dedicated agent/command wrapper. Reuse supplied answers and ask at most one unresolved question per turn.
- Inspect existing state before proposing changes; preview/read-and-merge while preserving unknown fields and unrelated content. Continue only selected layers, skip completed setup phases and retain prior authorization.
- Missing installed capabilities, dependency/model execution and name conflicts are explicit decisions. Cancel stops pending writes and reports any earlier applied work.
- Explicit operational requests use their existing modes without restarting setup; do not claim model-measured routing or conversation quality from static scenarios.

Interactive routing additions and task-success scenarios are verifier-authored supplements in evals; the original archived 192 routing cases/outcomes remain intact.
