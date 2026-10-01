# Evolution log

## one-approver-per-pipeline completion review

Observed deletion of APPROVED or VERIFY_EXIT signed evidence still allowed a production push.
Two real hook regressions failed before the fix. The consumer now maps proof-bearing history
edges to exactly one consumed request and checks the exact stored signed challenge. Isolation
status also no longer claims readiness from account existence; its regression failed before the fix.
Focused isolation verification: 14 passed; dual-identity verification: 7 passed before expanded cases.
Remaining same-account exposure is OPEN in map-debt.md. Broad conventions audit findings are
not represented as a clean result. No production key was read or used by the agent.

## Plugin installer nested pointer resolution

Fixed a platform-portable install bug: textual Git symlink pointers that targeted another
pointer were copied unresolved. The installer now follows pointer chains, detects cycles, and
preserves the missing-target fallback. Added regression tests for nested pointers and cycles;
the exact downstream SharePoint chain now copies the canonical script body. Plugin-manager
tests: 61 passed.
