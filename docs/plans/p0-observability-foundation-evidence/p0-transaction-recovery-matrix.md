# P00 Transaction and Recovery Matrix

Owner: Agentic OS control-plane maintainer
Reviewer: independent reviewer selected by the user
Status: PENDING_REVIEW — binding draft; not approved for runtime use

Each durable recovery record is keyed by generation and the full observation
correlation tuple. No row authorizes automatic provider re-execution.

| Boundary or failure | Atomic owner | Durable record | Report status | Retry / dispatch rule |
| --- | --- | --- | --- | --- |
| Expectation commit succeeds, before spawn | dispatch coordinator | committed `expected` row plus `dispatch_intent` timestamp | `dispatch_intent_recorded` | on restart, no start record means `dispatch_not_started`; do not assume a spawn occurred |
| Pre-dispatch expectation commit fails | adapter/caller | failure row, or caller-visible recovery context if persistence is unavailable | `pre_dispatch_commit_failed` | block dispatch; pause for authorized disposition |
| Spawn request fails before child creation | dispatch coordinator | `spawn_failed` error linked to expectation | `spawn_failed` | no provider retry without user/policy decision |
| Spawn is issued, but start record is not durably recorded | dispatch coordinator + producer | `dispatch_intent` plus caller-visible launch context | `spawn_status_unknown` | on restart discover final artifact; if none, record `start_unconfirmed_no_artifact` and require authorization before any retry |
| Child start is durably recorded, no artifact | producer + adapter | `started` row with artifact destination | `artifact_missing` | restart records `started_no_artifact`; no automatic rerun |
| Producer interruption while writing temporary artifact | producer | unique temporary-name/reference and interruption context when available | `artifact_partial` | consumer ignores temp; never publishes/ingests it; cleanup/retry needs authorization |
| Artifact malformed/schema-invalid | ingest validator | digest/path-safe reference + validation error | `artifact_invalid` | quarantine; never rerun provider automatically |
| Process exits during final publish | producer/caller | process outcome, destination, and publish phase | `publish_outcome_unknown` | on restart validate an existing final artifact; otherwise record metadata missing; never overwrite/re-run automatically |
| Process succeeds, metadata write fails | producer/caller | process outcome + write-failure context | `artifact_missing` | never report complete usage |
| Artifact writes, ingest commit fails | ingest adapter | artifact identity + ingest error | `ingest_pending` | replay ingest only |
| SQLite transaction/commit crashes or raises ambiguously | SQLite transaction owner | operation key/digest and original error through durable row or caller channel | `commit_outcome_unknown` | reopen and query canonical key/digest: classify `committed`, `ingest_pending`, or `ambiguous`; never rerun provider |
| Transition commits, staging fails | transition owner | receipt + measurement failure context | `coverage_incomplete` | block dependent dispatch; reconcile |
| Staging commits, receipt fails | transition owner | uncommitted staged observation | `transition_uncommitted` | do not fabricate a receipt |
| Same digest redelivery | ingest adapter | original + duplicate receipt/count | `observed` | idempotent |
| Different digest redelivery | ingest adapter | both references + conflict | `ambiguous` | quarantine and review |
| Restart discovery | recovery reconciler | immutable ledger/artifact scan result and classification time | one of `dispatch_not_started`, `start_unconfirmed_no_artifact`, `started_no_artifact`, `artifact_partial`, `artifact_invalid`, `ingest_pending`, or `observed` | classify only from recorded rows and safe final artifacts; never infer execution success |
| Reset/disk-full/corruption/identity error | generation owner/failing caller | snapshot or original error/context | generation-specific/`measurement_failure` | preserve; pause dependent work |

Reconciliation may mark a started attempt incomplete or pending. It cannot infer
a result, create a receipt, or rerun ambiguous external work. Every row needs a
deterministic fixture and test before implementation acceptance.
