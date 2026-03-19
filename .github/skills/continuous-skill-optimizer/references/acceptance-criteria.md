# Acceptance Criteria: continuous-skill-optimizer

1. The optimizer must run an explicit baseline iteration before proposing modifications.

2. Every iteration must write a row to `evals/results.tsv` with decision `keep`, `discard`, or `crash`.

3. On crash/timeout during improvement, the loop must continue from the last known good description and record the failure reason.

4. The optimizer must not auto-apply generated changes to source `SKILL.md` unless explicitly requested by the caller.
