# Task 0007: BL-003: Fix race condition in parallel INNER/PEER results.tsv writes

## Objective
PEER_AGENT finished before INNER_AGENT in L003, wrote results.tsv first. INNER read last_score from PEERs row instead of prior cycle. Tie case (0.9>=0.9) showed DISCARD due to float comparison after TSV round-trip. Options: file lock, serialize agents, or change >= to > as immediate mitigation.

## Acceptance Criteria
Two parallel agents writing results.tsv produce correct KEEP/DISCARD verdicts. Tie score case has unambiguous classification.

## Notes
