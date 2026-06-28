# Mode 2: Single-shot QA Protocol

Another agent proposes a change → this skill validates it → KEEP or DISCARD.

Execute these phases in strict order:

## Phase 1: Context Acquisition & Mutation Constraint

1. Read the **proposed** changes/diff from the invoking agent (or standard input).
2. Verify that the proposal changes only **ONE variable** (e.g., changing one trigger phrase, or one instruction). Bulk rewrites violate the isolation constraint and must be rejected immediately.
3. Write the proposed changes to the underlying `SKILL.md` file temporarily.

## Phase 2: Headless Evaluation

Do NOT attempt to "mentally simulate" whether the skill will route correctly. Subjective checking is banned.
Run the loop gate against the target skill. It calls `eval_runner.py` internally and compares against the baseline:
```bash
python ./scripts/evaluate.py --skill path/to/skill-folder --desc "what changed"
```
`eval_runner.py` is a pure scorer — it only outputs metrics, it does not determine KEEP/DISCARD. `evaluate.py` is the gate that reads the baseline, compares, writes one row to `<target-skill>/evals/results.tsv`, and exits 0 (KEEP) or 1 (DISCARD).

## Phase 3: The Revert/Reset Protocol

1. Check the exit code from `evaluate.py` (0 = KEEP, 1 = DISCARD) after overfitting gate.
2. **If `DISCARD`**: `evaluate.py` already ran `git checkout -- SKILL.md` automatically before exiting 1. Verify the file is restored (read its frontmatter). Report the `DISCARD` failure to the orchestrator with the score delta.
3. **If `KEEP`**: The change objectively improved the skill against the baseline. Leave the file on disk, proceed to Phase 4.

## Phase 4: Commit & Report

1. **If `KEEP`**: Commit the accepted change immediately — do not batch multiple KEEPs into one commit.
   ```bash
   git add path/to/SKILL.md
   git commit -m "keep: score=<score> f1=<f1> <desc>"
   ```
2. **If `DISCARD`** (already reverted in Phase 3): Report the failure scores:
   ```
   DISCARD: score=<score> (baseline=<baseline>, delta=<delta>)  f1=<f1> (baseline_f1=<baseline_f1>)
   desc: <what was tried>
   ```
3. In both cases, append a one-line summary to the loop ledger if you're in Mode 1:
   ```
   Iteration <N>: <KEEP|DISCARD>  score=<X>  delta=<+/-Y>  f1=<Z>  — <desc>
   ```
   *Note: Best practice is to also emit kernel intent/result events via `context/kernel.py` here to provide an observability trail for morning backport reviews.*
4. If a target score threshold was set (e.g. `--until-score 0.95`) and `status == KEEP`: check whether `score >= threshold`. If yes, stop the loop and notify the user.
