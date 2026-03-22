# Task 0006: BL-002: Guard eval_runner.py against out-of-context calls (spurious TSV rows)

## Objective
Sub-agents ran eval_runner.py during survey writing without --desc, producing 2 spurious Manual iteration rows in results.tsv. Add --cycle-id optional flag with stderr warning when absent. Rows without cycle-id should be visually distinguishable.

## Acceptance Criteria
eval_runner.py warns to stderr when --desc or --cycle-id absent. Spurious rows labelled unscoped in TSV. Progress chart handles unscoped rows separately.

## Notes
