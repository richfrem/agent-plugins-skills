# P00 Producer Artifact Contract

Owner: CLI Agents maintainer
Reviewer: independent reviewer selected by the user
Status: PENDING_REVIEW — binding draft; not approved for runtime use

The standalone producer may accept `--measurement-artifact <path>` plus explicit
`--task-id`, `--task-generation-id`, `--run-id`, `--invocation-id`, and
`--attempt-id`. Without the artifact option it preserves current output and exit
behavior and never imports Agentic OS.

The artifact is UTF-8, versioned JSON no larger than 1 MiB with only allowlisted
timing, exit, usage, requested/observed model, producer/install identity, and
correlation fields. It excludes prompts, output, stderr, secrets, source,
arbitrary environment values, and unrestricted paths. It uses the P00 canonical
SHA-256 digest. `producer_namespace`, producer version, and schema version are
required; an unobservable install fingerprint is explicitly unavailable.

## Concrete JSON shape

The root object has `additionalProperties: false` and requires `artifact_kind`,
`schema_version`, `capture`, `producer`, `correlation`, `event`, `execution`,
and `usage`. `artifact_kind` is the literal `p0_measurement_observation`;
`schema_version` is the literal `1.0-draft` until a reviewed version supersedes
it. The following nested objects are also closed:

| Object | Required fields and types | Nullable fields / rule |
| --- | --- | --- |
| `capture` | `method`, `captured_at_utc`, `source_runtime` strings; `sanitization` string | `source_runtime_version`: string or `null`; null requires non-empty `source_runtime_version_unavailable_reason`; that reason is prohibited when version is a string |
| `producer` | `namespace`, `version` strings | `install_fingerprint`: string or `null`; null requires non-empty `install_fingerprint_unavailable_reason`; that reason is prohibited when fingerprint is a string |
| `correlation` | `task_id`, `task_generation_id`, `run_id`, `invocation_id`, `attempt_id` non-empty strings | none |
| `event` | `event_id` UUIDv7 string, `occurred_at_utc` timestamp string, `coverage_state` enum, `canonical_digest` 64-lowercase-hex string | production digest is non-null; a draft fixture may use null only with non-empty `canonical_digest_unavailable_reason`, which is prohibited for a non-null digest |
| `execution` | `exit_code` integer, `duration_ms` non-negative integer, `duration_provenance` enum, `requested_model` string | `observed_model`: string or null; null requires non-empty `observed_model_unavailable_reason`, which is prohibited for a string model |
| `usage` | `provenance` enum (`reported`, `measured`, `estimated`, `unavailable`) | each token field is non-negative integer or null; `unavailable_reason` is required iff any token field is null; `unavailable` provenance requires all token fields null |

No number may be a decimal, exponent, `-0`, or non-finite value; all strings are
UTF-8 and bounded by the 1 MiB artifact limit. `coverage_state` is one of
`expected`, `started`, `observed`, `artifact_missing`, `artifact_invalid`,
`ingest_pending`, `ambiguous`, or `unavailable`. Unknown values are represented
by their documented null-plus-reason pair, never an omitted required field.

`duration_provenance` is exactly `reported`, `measured`, `estimated`, or
`synthetic_fixture`. `synthetic_fixture` is permitted only for a draft fixture
whose `capture.method` contains `fixture`; production artifacts must use one of
the first three values. `usage.provenance = unavailable` requires all four token
fields (`input_tokens`, `output_tokens`, `cached_tokens`, `reasoning_tokens`) to
be null. For any other provenance, a missing token is null with its named reason,
and any integer token is a recorded value rather than an inferred zero.

Destination behavior is fail-closed. Validate a caller-authorized parent/root;
reject an existing final destination, final symlink, symlinked parent component,
non-regular entry, root escape, `EXDEV`, partial file, and uncertain atomicity.
Use an atomic no-replace primitive supplied by the platform (for example
`renameat2(..., RENAME_NOREPLACE)` where available) after creating a unique
mode-`0600` temporary regular file in the final directory, writing/fsyncing it,
and fsyncing the directory after publish. A platform without an atomic no-replace
primitive has no safe publish fallback in P0: fail `atomic_no_replace_unavailable`
rather than use check-then-rename or overwrite. The existence check before and
after temp creation is advisory only; an `EEXIST` from the no-replace primitive
wins any TOCTOU race and is recorded as `destination_collision`. No overwrite,
replace, link-following, or copy fallback is allowed. Ingest ignores
temporary/partial files; their cleanup is separately authorized.

If the CLI succeeds but artifact creation fails, report
`CLI_SUCCESS_METADATA_FAILED` separately. Do not impersonate process failure or
claim complete usage. Consumer-invalid artifacts are `artifact_invalid` and never
automatically re-run the provider. Tests cover absent option, allowlist/digest,
oversize, collision, parent/final symlinks, interruption, permission, and EXDEV.
Independent review is required before this artifact can be marked PASS.
