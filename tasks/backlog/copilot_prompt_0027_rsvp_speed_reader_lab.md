# RSVP Speed Reader Eval Lab Setup & Execution

You are the Copilot CLI agent. Your goal is to orchestrate the improvement lab for the `rsvp-speed-reader` plugin.
Follow these steps EXACTLY. Use the Write tool to write files directly — do not output delimiters.

## WS-1: Lab Isolation
Run the `os-eval-lab-setup` skill to create a sibling evaluation repository for `plugins/rsvp-speed-reader`.
Ensure the lab is completely isolated from the main `agent-plugins-skills` repository to prevent contamination of the main branch during the improvement cycle.

## WS-2: Metric Definition & Test Scaffold
1. In the isolated lab repository, create a headless scoring script `test_orp_engine.py` that imports `calculate_orp` from `skills/rsvp-reading/scripts/orp_engine.py`.
2. Define a golden dataset of 50 edge-case words (e.g., hyphenated, quotes, extremely long words, alphanumeric mixes, symbols) and their expected optimal recognition point (ORP) indices.
3. The script must output a single floating point number between 0.0 and 1.0 (accuracy percentage) to stdout.
4. Create/update `evals.json` in the lab to use this script as the quantitative benchmark for the skill.

## WS-3: Execute Improvement Loop
Invoke `os-improvement-loop` to run against the lab environment.
Enforce the following strict execution parameters:
- **Max Iterations:** Exactly 10
- **Mutation Constraint:** Instruct the loop explicitly: "For each iteration, mutate strictly ONE variable or logic block at a time to maintain scientific rigor. Do not rewrite the entire function."
Wait for the 10 iterations to conclude and verify that the results are appended to the experiment log.

## WS-4: Generate Improvement Report
Once the loop concludes and the results exist in `context/experiment-log/index.md`:
1. Run `os-improvement-report` to generate a visual chart/summary showing the score delta over the 10 iterations.
2. Save the final report to `context/experiment-log/rsvp-speed-reader-report.md`.

## COMPLETION_REPORT
When finished executing all workstreams, output the following exactly:
- Created isolated lab directory path
- Defined quantitative metric details (summary of the 50-word golden dataset approach)
- Result of the 10-iteration loop (final vs initial score)
- Path to the generated improvement report
