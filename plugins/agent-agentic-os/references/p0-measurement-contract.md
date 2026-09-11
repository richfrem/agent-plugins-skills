# P0 Measurement Contract (A01)

Status: DRAFT — P00 review input only; no runtime behavior is authorized by this file.

## Canonical observation

SQLite stores append-only canonical observations for the retention window.
Reports/views are rebuildable projections. An observation uses the P00 canonical
key `(producer_namespace, schema_version, event_id)` and SHA-256 canonical
payload digest. Same-key/same-digest redelivery is a no-op; same-key/different-
digest is an `ambiguous` integrity conflict that never overwrites the first
payload.

Every observation owns `task_id`, `task_generation_id`, `run_id`,
`invocation_id`, and `attempt_id`. It records requested and observed model/effort
separately, with source or runtime provenance. Unknown is `null` plus an
unavailable reason; numeric zero is a valid measured value.

## Metric semantics

Every metric records value, unit, provenance (`reported`, `measured`,
`estimated`, or `unavailable`), and scope. Provider counters retain provider
meanings; overlapping categories are not summed. Prompt bytes are not total model
context. Snapshot/delta/final/correction precedence is fixture-specific: an
authoritative final may supersede snapshots for aggregation while earlier
observations remain retained and linked.

## Settlement, recovery, and privacy

Usage is settled only when fixture-defined sources are compatible and final or
otherwise complete. Incompatible values remain unsettled and visible. Recovery
is generation/attempt-owned and may exist without a committed transition.
Pre-dispatch expectation commit failure blocks external dispatch. Invalid/missing
artifacts are explicit coverage states; reconciliation cannot infer results or
rerun ambiguous provider work.

Only allowlisted metadata crosses the CLI-Agent/Agentic-OS boundary as a
versioned artifact. Prompts, output, stderr, secrets, source, environment values,
and unrestricted paths are excluded. Retention begins with a 30-day diagnostic
target, growth/pressure review, preview-only cleanup, and no automatic deletion.
Backup/restore needs separate explicit authorization.

This contract cannot authorize lifecycle transitions or weaken receipt rules.
Expected unavailable fields do not force a prompt; collector, persistence,
corruption, or identity failure pauses dependent work for contextual direction.
