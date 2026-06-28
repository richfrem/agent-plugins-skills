# Setup: Start a New Experiment

## Step 0 — Hardened Bootstrap (Fresh Repo Only)

Before running any loops in a new environment, ensure it is clean and correctly linked:
1. **Check Git Remote**: `git remote -v`. If blank, ask the user for the repo URL.
2. **Initialize Local Git**: `git init && git add . && git commit -m "init"`.
3. **Delete Old Config**: `rm -rf .agent .agents .gemini .claude`.
4. **Install Skill**: Ensure **os-eval-runner** is installed. See [INSTALL.md](https://github.com/richfrem/agent-plugins-skills/blob/main/INSTALL.md).
5. **Verify Python 3**: `python --version` (must be 3.8+).

## Step 1 — Deploy templates into your experiment directory

```bash
python ./scripts/init_autoresearch.py \
    --experiment-dir <path/to/your-experiment-dir> \
    --mutation-target SKILL.md   # or any filename being mutated
```
This creates `references/program.md`, `evals/evals.json`, and `evals/results.tsv` in your experiment dir. Templates stay untouched.

## Step 2 — Edit the deployed files

- `references/program.md` — fill in the Notes section: what are you optimizing, target score, max iterations
- `evals/evals.json` — replace the `REPLACE` placeholders with real test inputs and `should_trigger` values

## Step 3 — Establish baseline and start the loop

*(Best Practice: Run a functional CLI heartbeat using `run_agent.py` and the cheapest available model (see `references/cheapest_models.md`) to verify end-to-end connectivity before starting a long loop.)*
```bash
python ./scripts/evaluate.py \
    --skill <path/to/experiment-dir> \
    --baseline --desc "initial baseline"
git add <path/to/experiment-dir>/evals/
git commit -m "baseline: initial evaluation snapshot"
git push origin main
```
# Pass the FOLDER path, not a specific file — the scorer evaluates the whole skill folder.
# --baseline intentionally bypasses the SHA256 check, so you can safely re-baseline
# after updating evals.json with better test cases.
# Always PUSH your baseline to ensure the remote repository has the results.tsv and .lock.hashes.
