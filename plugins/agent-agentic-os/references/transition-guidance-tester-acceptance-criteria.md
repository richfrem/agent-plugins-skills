# Acceptance Criteria: transition-guidance-tester

## Positive scenarios

- Runs a deterministic simulation for one requested transition.
- Grades approval, guidance summary, required questions, target state, and commit authorization.
- Reports evidence for each criterion and stops after three failed attempts.
- Does not weaken grading criteria to hide a failed transition.

## Negative scenarios

- Rejects an unknown transition instead of silently testing a different edge.
- Does not run the full regression suite unless `--all` is explicitly requested.
- Escalates after the third failed attempt rather than retrying indefinitely.
