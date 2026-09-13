# P0 Baseline Protocol (A20)

Status: DRAFT — protocol only. No live baseline is authorized or represented.

## Objective

Run one bounded local task to test whether the pipeline can guide a user through
contract validation, gap resolution, informed confirmation, and the next legal
transition without unnecessary friction. Use a frozen sanitized fixture and
produce machine-readable evidence plus a plain-language summary. The evidence
distinguishes available measurements from unavailable ones and exposes where
the pipeline makes the user guess, repeats itself, or cannot recover cleanly.
It does not prove productivity or a model/workflow comparison.

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

Acceptance means the retained observations support a report that lists contract
coverage, validation results, evidence, user confirmation, and any friction or
recovery gaps. Human acceptance is the final check for each transition summary;
each transition must also demonstrate that the user was told the next question,
action, or gate without having to guess it;
after each user answer or authorized agent action, the run must either continue
automatically or report a concrete blocker and recovery action; unexplained
idle time requiring a user reminder is a failed baseline case;
every user-facing response must state the current objective or phase, what just
happened, and what happens next;
the coverage manifest must record that continuity result and any friction;
revisions must re-enter the governed pipeline and be revalidated rather than
being applied as undocumented side-channel fixes;
it does not accept/verify task output or complete a native-runtime comparison.

## Future native comparison

Repeat equivalent tasks with the same acceptance contract, collection settings,
and comparable source/worktree identity. Compare compatible measured values only;
report missing parent/subagent/provider data as unavailable. One run is descriptive
rather than a performance conclusion.
