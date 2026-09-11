# P00 Event Identity Schema

Owner: Agentic OS control-plane maintainer
Reviewer: independent reviewer selected by the user
Status: PENDING_REVIEW — binding draft; not approved for runtime use

## Required identity

Every observation owns immutable `producer_namespace`, `producer_version`,
`schema_version`, `event_id`, `canonical_digest`, `task_id`,
`task_generation_id`, `run_id`, `invocation_id`, `attempt_id`, optional
`causal_parent_event_id`, `occurred_at_utc`, `ingested_at_utc`, and
`coverage_state`. The canonical key is `(producer_namespace, schema_version,
event_id)`. `event_id` is a UUIDv7 unique within that key namespace; every retry
gets a new `attempt_id` and never reuses an execution identity.

The digest is lowercase SHA-256 over the payload excluding the digest itself,
local ingest time, local file name, and local database row ID. It uses UTF-8
JSON with recursively sorted object keys, no insignificant whitespace, native
JSON booleans/null, and normalized RFC 3339 UTC timestamps. Schema/version and
producer identity are included in the payload. SHA-256 detects accidental local
corruption/collision; it is not a signature or tamper-proof provenance claim.

Same-key/same-digest redelivery is idempotent. Same-key/different-digest is an
integrity conflict: retain both payload references, mark `ambiguous`, and never
overwrite, merge, or select a winner automatically. A path is not an identity;
ingestion computes key and digest after secure validation. Different event IDs
remain distinct even when values match.

## Ownership and links

`producer_namespace` is a stable producer-assigned reverse-domain name (for
example `io.richfrem.cli-agents.codex`), not a model name. An observable install
fingerprint is separate and unavailable when unobservable. Requested/observed
model are separate allowlisted fields and never substitute for producer identity.

The observation owns its complete correlation tuple. Lifecycle transitions,
receipts, and reviews are optional evidence links only: no observation or
recovery record may require a foreign-key parent that reset can delete. This
preserves denied, uncommitted, and reset-era evidence.

## Acceptance evidence

- Fixtures prove canonical serialization and SHA-256 reproducibility.
- Tests prove idempotency, conflicting redelivery, namespace separation, and
  distinct retry attempts.
- Tests prove reset/deleted lifecycle rows cannot orphan observations.
- Independent review is required before this artifact can be marked PASS.
