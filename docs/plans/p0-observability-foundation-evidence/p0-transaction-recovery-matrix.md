# P00 Transaction and Recovery Matrix

Owner: Agentic OS control-plane maintainer
Reviewer: independent reviewer selected by the user
Status: PENDING_REVIEW — binding draft; not approved for runtime use

Each durable recovery record is keyed by generation and the full observation
correlation tuple. No row authorizes automatic provider re-execution.

| Boundary or failure | Atomic owner | Durable record | Report status | Retry / dispatch rule |
| --- | --- | --- | --- | --- |
| Expectation commit succeeds | measurement adapter | `expected` attempt | expected | dispatch permitted |
| Pre-dispatch expectation commit fails | adapter/caller | failure row, or caller-visible recovery context if persistence is unavailable | `pre_dispatch_commit_failed` | block dispatch; pause for authorized disposition |
| Process starts, no artifact | producer + adapter | `started` when available | `artifact_missing` | no automatic rerun |
| Artifact malformed/schema-invalid | ingest validator | digest/path-safe reference + validation error | `artifact_invalid` | quarantine; never rerun provider automatically |
| Process succeeds, metadata write fails | producer/caller | process outcome + write-failure context | `artifact_missing` | never report complete usage |
| Artifact writes, ingest commit fails | ingest adapter | artifact identity + ingest error | `ingest_pending` | replay ingest only |
| Transition commits, staging fails | transition owner | receipt + measurement failure context | `coverage_incomplete` | block dependent dispatch; reconcile |
| Staging commits, receipt fails | transition owner | uncommitted staged observation | `transition_uncommitted` | do not fabricate a receipt |
| Same digest redelivery | ingest adapter | original + duplicate receipt/count | `observed` | idempotent |
| Different digest redelivery | ingest adapter | both references + conflict | `ambiguous` | quarantine and review |
| Reset/disk-full/corruption/identity error | generation owner/failing caller | snapshot or original error/context | generation-specific/`measurement_failure` | preserve; pause dependent work |

Reconciliation may mark a started attempt incomplete or pending. It cannot infer
a result, create a receipt, or rerun ambiguous external work. Every row needs a
deterministic fixture and test before implementation acceptance.
