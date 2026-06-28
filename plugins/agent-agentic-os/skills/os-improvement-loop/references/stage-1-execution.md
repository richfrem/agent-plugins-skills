# Stage 1: INNER_AGENT Execution Protocol

Every time INNER_AGENT receives `task.assigned`, it MUST:

1. **Read the strategy packet** at the path in the event summary.
2. **Execute the assigned work** — edit target skill, workflow doc, or artifact.
3. **Emit friction events immediately** when hitting uncertainty, wrong syntax, or needing help.
4. **Run the eval engine** using the os-eval-runner canonical scripts.
   The experiment dir must have been bootstrapped by `os-eval-lab-setup` first
   (deploys `evals/evals.json` with `should_trigger` boolean schema, `evals/results.tsv`,
   and `references/program.md`).

   **Option A — pure scorer** (get JSON metrics, decide KEEP/DISCARD manually):
   ```bash
   python ./scripts/eval_runner.py --skill path/to/target/
   # Pass the FOLDER path, not a file. Output: JSON with accuracy + F1 scores.
   ```

   **Option B — loop gate** (evaluate.py returns exit 0=KEEP, 1=DISCARD automatically):
   ```bash
   python ./scripts/evaluate.py --skill path/to/target/
   # Exit 0 = KEEP (accuracy AND F1 >= baseline). Exit 1 = DISCARD. Exit 2 = path error.
   # Exit 3 = tampered env (.lock.hashes mismatch) — delete .lock.hashes, re-run --baseline.
   ```
   See `os-eval-runner` Troubleshooting section for exit code reference, keywords footgun,
   and 4-character word floor.

5. If DISCARD: revert edit, note failure in output file, emit `task.complete --status fail`.
6. Write output to `handoffs/out-${CID}.md`.
7. **Complete the Post-Run Self-Assessment Survey** (see Stage 4.2).
8. **Before emitting `task.complete`**, close every friction event emitted this cycle with a `type: friction.resolved` event (outcome: `FIX`, `MAP_DEBT`, or `ESCALATE`).
9. Emit `task.complete` including score, output path, and survey path in summary.
