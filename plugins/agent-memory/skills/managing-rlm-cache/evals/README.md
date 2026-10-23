# Evaluation provenance

`evals.json` preserves every source routing prompt with source skill, zero-based source index, and original outcome.
Semantic reclassification is explicit in `reclassification_reason`.

`legacy/` holds byte-identical original evals and historical results. Those scores describe the former micro-skills and are not a baseline for this consolidated skill.
The new `results.tsv` contains a header only because no model routing run has been performed.
See the migration eval-preservation report for the hash inventory and each changed expectation.
