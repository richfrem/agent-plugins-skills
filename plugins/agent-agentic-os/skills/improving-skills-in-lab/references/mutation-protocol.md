# Mutation Protocol: propose, score, keep or discard

How the `loop` mode produces one change per iteration. Scoring is never done here: every candidate
goes to the `score` mode.

## Preconditions

1. The target folder has the target skill's `program.md` (goal, locked files, stop rule), `evals/evals.json` (`should_trigger` schema) and a baseline row in `evals/results.tsv`. If any is missing, run the `setup` mode first.
2. Cap iterations when the human gives a cap ("run 10 iterations", "until score 0.95"). Without a cap, the session limit in [lab-limits.md](lab-limits.md) applies.

## Each iteration

**Step A - Classify the failure.** Read the latest row in `<target>/evals/results.tsv` and the newest file in `<target>/evals/traces/`. Name the dominant failure: `false_positive`, `false_negative` or `ambiguity`.

**Step B - Propose one change.** Prefer a cheap external proposer (models in [cheapest_models.md](cheapest_models.md)).
The proposer prompt lives in `<experiment-dir>/references/copilot_proposer_prompt.md`; read it each
iteration, do not rebuild it inline. If it is missing, run the `setup` mode to redeploy it.

Call through the CLI agent skills, not raw CLI strings (quoting and piping are fragile):
- `cli-agent` with `--cli copilot` (default), or `--cli agy` if the plan says so.
- Self-propose only if neither is available.

Pass the prompt file, the target `SKILL.md`, an output path and a one-line brief naming the failure
type. Copy the output over `SKILL.md`. If the output is identical to the current file, re-prompt with
"try a different approach" and emit a friction event through `context/kernel.py`.

**Step B.1 - Evolve the proposer (second-order mutation).** After 3 consecutive DISCARDs with the same
failure type, suspect the proposer prompt. Propose one focused edit to `copilot_proposer_prompt.md`
(a constraint, a sharper failure description, a tighter output format) and gate it the same way.
Other second-order targets when stalled: the target skill's `program.md` if its goal or locked-file list no
longer matches what the evals test. These rank below direct skill mutations.

**Step C - Score.** Invoke the `score` mode on the target folder with a one-line description.
- KEEP (exit 0): commit the single change (`keep: score=<s> <desc>`); push only if the lab plan says to.
- DISCARD (exit 1): already reverted by the scorer; log the row and continue.
- Exit 2 or 3 is not a verdict: stop and read the scorer's troubleshooting reference.

**Step D - Record.** Append one ledger line per iteration and emit kernel events for the morning review:

```
Iteration <N>: <KEEP|DISCARD>  score=<X>  delta=<+/-Y>  f1=<Z>  - <desc>
```

Stop on the human's cap, the target score, three consecutive DISCARDs (strategy review), or the
session limit. Then go to close ([stage-4-close.md](stage-4-close.md)).
