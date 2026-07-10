# Mode 1: Autoresearch Loop (Iterative Improvement)

The agent drives N iterations against a target skill. Start with:
```
"Run the autoresearch loop on <path/to/target-skill> for N iterations"
```

The agent will execute these steps:

1. **Read program spec**: Read `<target-skill>/references/program.md` (goal + locked files + NEVER STOP). If missing, run `python ./scripts/init_autoresearch.py --skill <target-path>` first.
2. **Establish baseline**: If none exists, run `python ./scripts/evaluate.py --skill <path/to/skill-folder> --baseline`
3. **Loop N times** (default: run until told to stop per NEVER STOP directive). Each iteration:

   **Step A — Classify failure:** Read the latest row in `<skill>/evals/results.tsv` and the most recent trace file in `<skill>/evals/traces/`. Identify the dominant failure type: `false_positive`, `false_negative`, or `ambiguity`.

   **Step B — Propose via CLI (preferred) or self:** Delegate the mutation to an external CLI proposer for cheap, fast iteration.

   The proposer prompt lives in `<experiment-dir>/references/copilot_proposer_prompt.md`. Read it each
   iteration — do not rebuild inline. If the file is missing, scaffold it first:
   ```bash
   python ./scripts/init_autoresearch.py \
       --experiment-dir <experiment-dir> --mutation-target <filename>
   ```

   Call pattern (incorporating Triple-Loop Orchestrator stability patterns):
   ```bash
   # Explicitly delegate to a cost-effective CLI sub-agent (see references/cheapest_models.md for current model names)
   # Use run_agent.py for stability instead of raw CLI calls to avoid quoting/piping fragility
   python .agents/skills/copilot-cli-agent/scripts/run_agent.py \
     <experiment-dir>/references/copilot_proposer_prompt.md \
     <skill>/SKILL.md \
     /tmp/proposed-skill.md \
     "Optimize agentic skill routing accuracy. FAILURE TYPE: <failure_type>. Summary: <one-sentence description of what the last iteration got wrong>"
     
   cp /tmp/proposed-skill.md <skill>/SKILL.md
   ```
   Use `agy-cli-agent` instead of `copilot-cli-agent` if specified (the standalone `gemini` CLI was shut down June 2026 — `agy` is the replacement). Fall back to self-proposing only if neither CLI is available. If using raw CLI due to lack of `run_agent.py`, ensure prompts are piped appropriately. If the proposed file is identical to current, re-prompt with "try a different approach" and log a friction event via `context/kernel.py`.

   **Step B.1 — Evolve the proposer prompt (second-order mutation):**
   After 3 consecutive DISCARDs with the same failure type, consider that the *prompt itself* may be
   the problem — not the skill. Propose one focused improvement to `copilot_proposer_prompt.md`
   (e.g. add a constraint, clarify the failure pattern, sharpen the output format). Gate it the same
   way: apply, run the loop, KEEP or revert. A KEEP on a prompt change means future iterations have
   a stronger proposer.

   Other second-order mutations to consider when the loop stalls:
   - **`references/program.md`** — if the spec's goal or locked-files list has become ambiguous or
     misaligned with what the evals actually test, proposing a clarification here can unblock progress.
   - **`copilot-cli-agent/SKILL.md`** — if the Copilot CLI skill description is missing patterns you
     rely on, improving it here benefits all future loops that use this proposer.

   Second-order mutations are lower priority than direct skill mutations. Only pursue them when the
   primary mutation target has stalled (3+ consecutive DISCARDs or diminishing score deltas).

   **Step C — Eval gate:**
   ```bash
   python .scripts/evaluate.py --skill <path/to/skill-folder> --primary-metric <metric> --desc "what changed"
   ```
   - exit 0 (KEEP): `git add . && git commit -m "keep: score=X <desc>" && git push origin main`
   - exit 1 (DISCARD): already auto-reverted, move to next iteration silently

To cap iterations, the human specifies: "run 10 iterations" or "run until score reaches 0.95".
The NEVER STOP directive in `program.md` means the loop has no built-in termination — only a human stop or a target threshold ends it.
