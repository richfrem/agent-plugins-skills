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

The digest is lowercase SHA-256 over the producer artifact after removing only
`event.canonical_digest`. Local ingest time, file name, and database row ID are
not producer-artifact fields and therefore never enter this input. No other
field is silently removed. Schema/version and producer identity are included.
SHA-256 detects accidental local corruption/collision; it is not a signature or
tamper-proof provenance claim.

## Deterministic canonicalization procedure

The producer and consumer implement this exact procedure before calculating or
validating a digest:

1. Decode bytes as strict UTF-8 and parse one JSON object. Reject duplicate
   object keys, non-finite numbers, trailing non-whitespace bytes, and fields
   outside the closed producer schema.
2. Require the P00 typed schema. All P00 counters and durations are integers;
   a JSON number must be an integer in `[-9007199254740991, 9007199254740991]`.
   Decimal, exponent, `-0`, `NaN`, and `Infinity` representations are rejected.
   Thus each accepted number serializes as its shortest base-10 integer with no
   leading plus or zero (except `0`).
3. Normalize exactly these producer timestamps: `capture.captured_at_utc` and
   `event.occurred_at_utc`. Parse RFC 3339 with an explicit `Z` or numeric UTC
   offset; reject leap seconds, parse failures, and fractional seconds with more
   than six digits (do not round or truncate). Convert to UTC and serialize as
   `YYYY-MM-DDTHH:MM:SS.ffffffZ`, with exactly six fractional digits, padding a
   shorter accepted fraction with zeroes. The consumer-created `ingested_at_utc`
   is outside the digest input.
4. Remove `event.canonical_digest`; preserve `null`, booleans, strings, arrays,
   and objects otherwise. Sort every object by Unicode code-point order of its
   keys. Decode input escapes into Unicode scalar values and reject unpaired
   UTF-16 surrogates. Emit compact UTF-8 JSON using `,` and `:` separators and
   no insignificant whitespace. Escape only `U+0022` as `\"`, `U+005C` as
   `\\`, and each `U+0000`–`U+001F` control character as lowercase `\u00xx`;
   emit every other Unicode scalar as its UTF-8 bytes (including `/`, non-ASCII,
   and `U+2028`/`U+2029`).
5. SHA-256 the emitted bytes and write 64 lowercase hex characters into
   `event.canonical_digest`. Validation repeats steps 1–4 and compares the
   resulting digest in constant time. Any parse, type, timestamp, or digest
   failure is `artifact_invalid`, never a guessed normalization.

The fixture's explicit `null` digest is permitted only because it is labelled a
draft contract fixture, not a publishable producer artifact. A production
artifact must carry a computed digest.

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
