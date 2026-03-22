# Task 0004: BL-004: Add LLM Judge to Eval Gate (llm_routing_score always N/A)

## Objective
Populate llm_routing_score column in results.tsv. Every KEEP/DISCARD verdict is currently keyword-only. F1 gate partially mitigates but doesnt add semantic quality judgment. Add optional --llm-judge flag to eval_runner.py for Standard Cycle runs.

## Acceptance Criteria
llm_routing_score column populated on Standard Cycle runs. Keyword-only mode still available for Fast Cycle. KEEP/DISCARD optionally incorporates LLM score.

## Notes
