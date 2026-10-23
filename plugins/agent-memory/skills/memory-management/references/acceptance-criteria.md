# Acceptance Criteria: Memory Management

## Preserved Contract

The [detailed memory-management criteria](memory-management-acceptance-criteria.md) remain authoritative for session boot, promotion/demotion, ordered lookup and session sealing. This index adds navigation and portability checks without replacing or weakening those criteria.

## Portability and Isolation

- Read/write the consumer project's memory, wiki and audit trace locations; do not treat the installed skill folder or source repository as the consumer's persistent state.
- Keep native memory lookup independent of RLM, vector databases, Obsidian and external daemons; optional retrieval layers do not become mandatory dependencies.
- Preserve confidence labels/decay, asymmetric persistence and user confirmation requirements in the retained workflow.
- Report missing or stale memory individually; preserve historical evidence rather than silently deleting it.
- Resolve this skill's reading resources through actual skill-local files, with no pointer stubs or dependence on source materialization.

## Evidence

Run the existing memory-layer test suite unchanged, verify its retained skill path and line budget, and inspect real local resource links. Use temporary consumer data for any write probe. Structural/test passes do not demonstrate that a real user session was booted, promoted/demoted or sealed.

## Conversation continuity

Run memory requests directly in the current conversation and reuse known session context. Do not require a dedicated memory agent, command wrapper or unrelated retrieval-layer setup. The preserved detailed boot/promotion/demotion/sealing criteria remain unchanged.
