# P00 Reset-Generation Model

Owner: Agentic OS control-plane maintainer
Reviewer: independent reviewer selected by the user
Status: PENDING_REVIEW — binding draft; not approved for runtime use

`task_id` identifies a logical task. `task_generation_id` identifies one
execution incarnation, is allocated before its first dispatch/expectation, is
globally unique, and is never reused after reset, cancellation, or recovery.

An append-only `task_generations` record owns task/generation IDs,
`created_at_utc`, creation cause, reset reason, and an initial-seed/source
fingerprint. Each observation copies its generation ID. Each recovery record is
owned by generation and attempt, including pre-dispatch commit failures,
invalid/missing artifacts, ingest failures, conflicts, and reconciliation
decisions; it carries `task_generation_id`, `run_id`, `invocation_id`, and
`attempt_id` even when no transition receipt committed.

Reset creates a new generation; it never mutates, relabels, or reattaches old
observations. Before the active view resets, store an immutable,
non-authoritative measurement summary snapshot with projection watermark and
incomplete/ambiguous attempts. Reports aggregate per generation first and must
name included generation IDs for a logical-task aggregate.

Measurement/recovery tables must not require foreign keys to active transitions,
transition receipts, verification receipts, or reviews that reset can remove.
Optional evidence links are nullable. Reset cannot cascade-delete observations,
generation records, invalid artifacts, or recovery decisions.

Acceptance requires reset/restart/replay tests, historical recovery visibility,
and a pre-dispatch failure report with no receipt. Independent review is required
before this artifact can be marked PASS.
