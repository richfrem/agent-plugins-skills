# Stage 1: INNER_AGENT Execution Protocol

Every time INNER_AGENT receives `task.assigned`, it MUST:

1. **Read the strategy packet** at the path in the event summary.
2. **Execute the assigned work** — edit target skill, workflow doc, or artifact.
3. **Emit friction events immediately** when hitting uncertainty, wrong syntax, or needing help.
4. **Score the change with `os-lab-scorer`** (never hand-score). The experiment dir must have
   been bootstrapped by `os-lab-setup` first (deploys `evals/evals.json` with `should_trigger`
   boolean schema, `evals/results.tsv`, and `references/program.md`).

   Invoke `os-lab-scorer` on the target folder (not a file). It runs `evaluate.py` and returns
   exit 0 = KEEP (accuracy AND F1 >= baseline), 1 = DISCARD (auto-reverted), 2 = path error,
   3 = tampered environment. Its troubleshooting reference covers exit codes, the keywords
   footgun and the 4-character word floor.

5. If DISCARD: revert edit, note failure in output file, emit `task.complete --status fail`.
6. Write output to `handoffs/out-${CID}.md`.
7. **Complete the Post-Run Self-Assessment Survey** (see Stage 4.2).
8. **Before emitting `task.complete`**, close every friction event emitted this cycle with a `type: friction.resolved` event (outcome: `FIX`, `MAP_DEBT`, or `ESCALATE`).
9. Emit `task.complete` including score, output path, and survey path in summary.
