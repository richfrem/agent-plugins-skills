# P0 Baseline Protocol (A20)

Status: DRAFT — protocol only. No live baseline is authorized or represented.

## Objective

Run one bounded local Codex-wrapper task using a frozen sanitized fixture and
produce evidence that distinguishes available measurements from unavailable ones.
It tests instrumentation feasibility only; it does not prove productivity or a
model/workflow comparison.

## Preconditions

1. The five P00 binding artifacts have independent approval and are marked PASS.
2. Contract and deterministic tests pass on the evaluated tree.
3. The user separately authorizes task, runtime/model/effort, spending bound,
   artifact location, and provider execution.
4. Capacity, permissions, and protected evidence paths are checked.

## Frozen input and procedure

Use a minimal non-sensitive fixture with explicit acceptance and no external side
effects. Record fixture digest, repository/worktree identity, observable producer
fingerprint, requested model/effort, and runtime. Authorization defines wall-clock,
retry, and provider/money bounds; this document does not invent them.

1. Persist pre-dispatch expectation; on commit failure, do not dispatch.
2. Execute exactly one authorized invocation.
3. Validate/ingest its allowlisted artifact, or record missing/invalid/pending
   state without automatic rerun.
4. Rebuild a report and compare fixture-defined expected fields.
5. Later authorized A21/A22/A23 reports record coverage, unavailable fields,
   timing, verification, and degradation honestly.

Acceptance means retained observations support a report that lists coverage gaps;
it does not accept/verify task output or complete a native-runtime comparison.

## Future native comparison

Repeat equivalent tasks with the same acceptance contract, collection settings,
and comparable source/worktree identity. Compare compatible measured values only;
report missing parent/subagent/provider data as unavailable. One run is descriptive
rather than a performance conclusion.
