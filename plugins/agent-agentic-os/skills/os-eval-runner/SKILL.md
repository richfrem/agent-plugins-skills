---
name: os-eval-runner
description: >
  Trigger: "evaluate this skill", "run autoresearch loop on", "optimize this skill".
  Use when an agent proposes a change to an existing skill and needs empirical validation.

  <example>
  Context: Start autonomous improvement loop on a skill.
  user: "Run the autoresearch loop on <SKILL_PATH> for 20 iterations"
  assistant: [triggers os-eval-runner, runs Mode 1 intake]
  </example>

  <example>
  Context: Incomplete optimize request.
  user: "Optimize the commit skill"
  assistant: [triggers os-eval-runner, runs Phase 0 intake interview]
  </example>

  <example>
  Context: `Triple-Loop Retrospective` proposes a skill edit.
  assistant: [autonomously] "Before I apply this description change, I'll run os-eval-runner to confirm."
  </example>

  <example>
  Context: An agent is asking for general information about a skill, not evaluating a proposed change.
  agentic-os-setup: "Tell me about the os-clean-locks skill."
  assistant: "It cleans up stale lock files..."
  
  </example>
argument-hint: "[path/to/SKILL.md or skill-name] [--iterations N] [--until-score 0.95]"
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

> **Prerequisites:** The target skill must be inside a **git repository** (`git init` first if needed). Python 3.8+ must be available as `python3`.

---

# Quick Start — Zero Context Guide

> Read this first. Everything below assumes you've completed these steps.

## What This Skill Does

`os-eval-runner` is a stateless evaluation engine. It contains:
- **Scripts** that score and gate iterations (`evaluate.py`, `eval_runner.py`, `init_autoresearch.py`)
- **Templates** — starter files you copy into whatever you want to optimize

It does NOT contain your experiment's results, history, or rules. Those live with your target.

## What Lives Where

```
os-eval-runner/                        <-- the evaluation ENGINE (this skill)
  scripts/
    evaluate.py          Loop gate: scores, KEEP/DISCARD, reverts, exits 0/1
    eval_runner.py       Pure scorer: reads target + evals.json, outputs JSON metrics
    init_autoresearch.py Scaffold tool: copies templates into your experiment dir
  ./assets/templates/autoresearch/               <-- TEMPLATES (master copies, never edit directly)
    program.md.template  Spec: goal, locked files, NEVER STOP
    evals.json.template  Test prompts: what inputs should/should not trigger your target
    results.tsv.template Schema header for the loop ledger

your-experiment-dir/                           <-- YOUR EXPERIMENT (wherever makes sense)
  <mutation-target>      The file being mutated each iteration (SKILL.md, .py, etc.)
  references/
    program.md           Deployed from template — your rules, your goal (edit this)
  evals/
    evals.json           Deployed from template — your test prompts (edit this)
    results.tsv          Deployed from template, then written by evaluate.py each run
    .lock.hashes         SHA256 snapshot of locked files — written by evaluate.py --baseline
    traces/              Per-iteration diagnostic JSON — written by evaluate.py each run
      iter_001_KEEP_score0.87.json    mutation diff + per-input routing verdicts
      iter_002_DISCARD_score0.71.json failure_reason for each incorrect routing
      milestone_025.md   Milestone summary — written every 25 iterations by generate_milestone.py
```

## Setup: Start a New Experiment (4 steps)

**Step 0 — Hardened Bootstrap (Fresh Repo Only):**
Before running any loops in a new environment, ensure it is clean and correctly linked:
1. **Check Git Remote**: `git remote -v`. If blank, ask the user for the repo URL.
2. **Initialize Local Git**: `git init && git add . && git commit -m "init"`.
3. **Delete Old Config**: `rm -rf .agent .agents .gemini .claude`.
4. **Install Skill**: Ensure **os-eval-runner** is installed. See [INSTALL.md](https://github.com/richfrem/agent-plugins-skills/blob/main/INSTALL.md).
5. **Verify Python 3**: `python3 --version` (must be 3.8+).

**Step 1 — Deploy templates into your experiment directory:**
```bash
python3 ./scripts/init_autoresearch.py \
    --experiment-dir <path/to/your-experiment-dir> \
    --mutation-target SKILL.md   # or any filename being mutated
```
This creates `references/program.md`, `evals/evals.json`, and `evals/results.tsv` in your experiment dir. Templates stay untouched.

**Step 2 — Edit the deployed files:**
- `references/program.md` — fill in the Notes section: what are you optimizing, target score, max iterations
- `evals/evals.json` — replace the `REPLACE` placeholders with real test inputs and `should_trigger` values

**Step 3 — Establish baseline and start the loop:**
```bash
python3 ./scripts/evaluate.py \
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

---

# Skill Improvement Evaluator

You are the OS Quality Assurance (QA) sub-agent. You are a **stateless evaluation engine**. You own no loop state, no experiment memory, and no program spec. All of that lives exclusively inside the TARGET experiment's directory.

## Ownership Boundary (Critical)

### What os-eval-runner owns (permanent, version-controlled with this skill)

| What | Location |
|---|---|
| Scoring scripts | `./scripts/evaluate.py`, `./scripts/eval_runner.py` |
| Scaffold script | `./scripts/init_autoresearch.py` |
| program.md **template** | `./assets/templates/autoresearch/program.md.template` |
| evals.json **template** | `./assets/templates/autoresearch/evals.json.template` |
| results.tsv **template** | `./assets/templates/autoresearch/results.tsv.template` |
| copilot proposer prompt **template** | `./assets/templates/autoresearch/copilot_proposer_prompt.md.template` |

### What lives with the target (deployed per experiment, most appropriate location)

The mutation target can be a SKILL.md, a Python script, a config file, or anything
with a clear metric. All experiment state deploys alongside the target — not here.

| What | Location |
|---|---|
| program.md (rendered from template) | `<experiment-dir>/references/program.md` |
| copilot proposer prompt (rendered from template) | `<experiment-dir>/references/copilot_proposer_prompt.md` |
| evals.json (rendered from template) | `<experiment-dir>/evals/evals.json` |
| results.tsv (loop ledger) | `<experiment-dir>/evals/results.tsv` |
| .lock.hashes (SHA256 snapshot) | `<experiment-dir>/evals/.lock.hashes` |

Where `<experiment-dir>` is the directory most natural to the target:
- Evaluating a skill → the skill's own directory (e.g. `.agents/skills/my-skill/`)
- Evaluating a Python module → the module's project directory
- Evaluating a config or model → wherever that experiment lives

**Deploy the templates to a new experiment:**
```bash
python ./scripts/init_autoresearch.py \
    --experiment-dir <path/to/experiment-dir> \
    --mutation-target SKILL.md   # or any filename being mutated
# Creates: <experiment-dir>/references/program.md  (rendered)
# Creates: <experiment-dir>/evals/evals.json        (rendered)
# Creates: <experiment-dir>/evals/results.tsv       (schema header)
```

You MUST read the spec from `<experiment-dir>/references/program.md`. You MUST NOT fall back to any `program.md` inside your own (`os-eval-runner`) directory. The `os-eval-runner/evals/` folder only exists for the meta-circular case where this skill is being evaluated as its own target.

## The 3-File Autoresearch Architecture

This skill strictly enforces the Karpathy 3-file autoresearch framework. Subjective LLM testing is strictly forbidden. You must rely entirely on headless, objective Python script evaluation to prevent Goodhart's Law exploitation.

1. **The Spec**: `<target-skill>/references/program.md` — owned by the target, never by you.
2. **The Mutation Target**: `<target-skill>/SKILL.md` — one variable per iteration, no bulk rewrites.
3. **The Immutable Evaluator**: `eval_runner.py` (pure scorer) + `evaluate.py` (loop gate) + `<target-skill>/evals/evals.json` (locked fixtures).

## Phase 0: Intake Interview

Run this before any evaluation or loop. If `$ARGUMENTS` provides enough information, confirm rather than re-ask. Otherwise ask each question that is unanswered.

**Q1 — What are you evaluating?**
Ask for the path to the skill folder (the directory containing SKILL.md). The mutation target
per iteration can be any file within that folder — SKILL.md, a script, a reference doc, etc.

- **Agent skill folder** (fully supported): `eval_runner.py` scores the whole folder holistically:
  routing accuracy from SKILL.md frontmatter keywords, structural heuristic per agentskills.io spec
  (name format, description length, `<example>` blocks, `scripts/*.py` py_compile, empty reference check).
- **Non-skill folders**: the agentskills.io heuristic will score poorly for targets without SKILL.md
  frontmatter. The architectural path for other target types is a per-experiment `eval_runner.py` template.

If not provided: "What skill folder do you want to optimize? Give me the path to the folder."

If not provided: "What file do you want to optimize? Give me the path to the file being mutated."

**Q2 — Where should the experiment files live?**
The experiment directory is where `references/program.md`, `evals/evals.json`, `evals/results.tsv`, and `evals/.lock.hashes` will be deployed. Each experiment gets its own isolated directory — never shared across targets.

- If the target is a SKILL.md → the skill's own directory is the natural experiment dir.
- If the target is a Python file or other → ask: "Where should I store the program spec and eval fixtures for this experiment? (e.g. the folder containing the file, or a dedicated experiment subdirectory)"

Confirm: "Experiment files will be stored at `<experiment-dir>/references/` and `<experiment-dir>/evals/` — is that right?"

**Q2b — What metric are you optimizing?**

Every skill has a different failure mode — pick the metric that matches:

| Metric | Flag | KEEP condition | Use when |
|---|---|---|---|
| `quality_score` | *(default)* | score ≥ baseline AND f1 ≥ baseline | General improvement |
| `f1` | `--primary-metric f1` | f1 ≥ baseline | Both precision AND recall matter |
| `precision` | `--primary-metric precision` | precision ≥ baseline, recall doesn't regress | Skill fires too often (false positives) |
| `recall` | `--primary-metric recall` | recall ≥ baseline, precision doesn't regress | Skill misses inputs (false negatives) |
| `heuristic` | `--primary-metric heuristic` | heuristic ≥ baseline | Routing correct; improve structure/docs |

Not sure which? Run `eval_runner.py --snapshot` first — it reports fp/fn rates and recommends PRECISION or RECALL focus.

**Q3 — What mode?**
- **Loop mode**: autonomous iterative improvement (agent proposes changes, scores them, loops)
- **QA mode**: validate one specific proposed change only

If the user said "optimize", "improve", "run the loop" → Loop mode.
If the user said "check this change", "validate", "evaluate this diff" → QA mode.
If unclear: "Do you want me to run an autonomous improvement loop, or validate a specific proposed change?"

**Q4 — (Loop mode only) How many iterations?**
Default: NEVER STOP (runs until told to stop).
Options: a fixed count ("10 iterations"), a score threshold ("until quality_score >= 0.95"), or open-ended.
If not specified: "How many iterations? Or run until a target score — e.g. stop when quality_score reaches 0.95?"

**Q5 — (Loop mode only) Does `evals.json` exist?**
Check `<experiment-dir>/evals/evals.json`.
- If exists: show the number of test cases.
- If missing: "No evals.json found. I'll scaffold it from the template — you'll need to replace the placeholder test cases before the loop starts."
  Run: `python3 ./scripts/init_autoresearch.py --experiment-dir <experiment-dir> --mutation-target <filename>`
  Then pause for the user to fill in the test cases.

**Q6 — (Loop mode only) Does `program.md` exist?**
Check `<experiment-dir>/references/program.md`.
- If exists: read it and show the goal. Confirm it still reflects what the user wants to optimize.
- If missing: "No program.md found. I'll scaffold it from the standard template:"
  ```bash
  python ./scripts/init_autoresearch.py \
      --experiment-dir <experiment-dir> \
      --mutation-target <filename>
  ```
  Then open `<experiment-dir>/references/program.md` and fill in the Notes section. Do NOT hand-write it — always generate from the template for consistent locked-files list and formula.

**Q7 — (Loop mode only) Does a baseline exist?**
Check `<experiment-dir>/evals/results.tsv` for a BASELINE row.
- If baseline exists: show the last BASELINE score and f1, iterations run, most recent score.
- If no baseline: "No baseline found. I'll establish one before starting the loop."

**After intake — confirm before executing:**
```
Target file:    plugins/.../my-skill/SKILL.md
Experiment dir: plugins/.../my-skill/         (program.md + evals live here)
Mode:           Loop (autoresearch)
Iterations:     20  (or: until quality_score >= 0.95  |  or: NEVER STOP)
Metric:         quality_score (default) with F1 guard
evals.json:     9 test cases  (or: MISSING — scaffold and fill before proceeding)
program.md:     exists — goal: maximize quality_score  (or: will scaffold)
Baseline:       score=0.8444 / f1=0.8333  (or: will establish)
History:        14 iterations, last score=0.8444 (3 KEEP, 2 DISCARD since baseline)

Proceed?
```

Do not start the loop or any evaluation until the user confirms.

---

## Two Modes

### Mode 1: Autoresearch Loop (overnight autonomous improvement)
The agent drives N iterations against a target skill. Start with:
```
"Run the autoresearch loop on <path/to/target-skill> for N iterations"
```
The agent will:
1. Read `<target-skill>/references/program.md` (goal + locked files + NEVER STOP). If missing, run `python3 ./scripts/init_autoresearch.py --skill <target-path>` first.
2. Establish a baseline if none exists: `python3 ./scripts/evaluate.py --skill <path/to/skill-folder> --baseline`
3. Loop N times (default: run until told to stop per NEVER STOP directive). Each iteration:

   **Step A — Classify failure:** Read the latest row in `<skill>/evals/results.tsv` and the most recent trace file in `<skill>/evals/traces/`. Identify the dominant failure type: `false_positive`, `false_negative`, or `ambiguity`.

   **Step B — Propose via CLI (preferred) or self:** Delegate the mutation to an external CLI proposer for cheap, fast iteration.

   The proposer prompt lives in `<experiment-dir>/references/copilot_proposer_prompt.md`. Read it each
   iteration — do not rebuild inline. If the file is missing, scaffold it first:
   ```bash
   python3 ./scripts/init_autoresearch.py \
       --experiment-dir <experiment-dir> --mutation-target <filename>
   ```

   Call pattern:
   ```bash
   cp <skill>/SKILL.md /tmp/current-skill.md
   cp <skill>/evals/evals.json /tmp/current-evals.json
   copilot -p "$(cat <experiment-dir>/references/copilot_proposer_prompt.md)

   ---CURRENT SKILL---
   $(cat /tmp/current-skill.md)

   ---EVAL SUITE---
   $(cat /tmp/current-evals.json)

   ---FAILURE ANALYSIS---
   Type: <failure_type>
   Summary: <one-sentence description of what the last iteration got wrong>" > /tmp/proposed-skill.md
   cp /tmp/proposed-skill.md <skill>/SKILL.md
   ```
   Use `gemini` instead of `copilot` if specified. Fall back to self-proposing only if neither CLI is available. If the proposed file is identical to current, re-prompt with "try a different approach".

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
   python3 .scripts/evaluate.py --skill <path/to/skill-folder> --primary-metric <metric> --desc "what changed"
   ```
   - exit 0 (KEEP): `git add . && git commit -m "keep: score=X <desc>" && git push origin main`
   - exit 1 (DISCARD): already auto-reverted, move to next iteration silently

To cap iterations, the human specifies: "run 10 iterations" or "run until score reaches 0.95".
The NEVER STOP directive in `program.md` means the loop has no built-in termination — only a human stop or a target threshold ends it.

### Mode 2: Single-shot QA (validate a proposed change)
Another agent proposes a change → this skill validates it → KEEP or DISCARD.
Phases below describe this mode.

---

## Execution Flow (Mode 2)

Execute these phases in strict order:

### Phase 1: Context Acquisition & Mutation Constraint
1. Read the **proposed** changes/diff from the invoking agent (or standard input).
2. Verify that the proposal changes only **ONE variable** (e.g., changing one trigger phrase, or one instruction). Bulk rewrites violate the isolation constraint and must be rejected immediately.
3. Write the proposed changes to the underlying `SKILL.md` file temporarily.

### Phase 2: Headless Evaluation
Do NOT attempt to "mentally simulate" whether the skill will route correctly. Subjective checking is banned.
Run the loop gate against the target skill. It calls `eval_runner.py` internally and compares against the baseline:
```bash
python3 ./scripts/evaluate.py --skill path/to/skill-folder --desc "what changed"
```
`eval_runner.py` is a pure scorer — it only outputs metrics, it does not determine KEEP/DISCARD. `evaluate.py` is the gate that reads the baseline, compares, writes one row to `<target-skill>/evals/results.tsv`, and exits 0 (KEEP) or 1 (DISCARD).

### Phase 3: The Revert/Reset Protocol
1. Check the exit code from `evaluate.py` (0 = KEEP, 1 = DISCARD).
2. **If `DISCARD`**: `evaluate.py` already ran `git checkout -- SKILL.md` automatically before exiting 1. Verify the file is restored (read its frontmatter). Report the `DISCARD` failure to the orchestrator with the score delta.
3. **If `KEEP`**: The change objectively improved the skill against the baseline. Leave the file on disk, proceed to Phase 4.

### Phase 4: Commit & Report
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
4. If a target score threshold was set (e.g. `--until-score 0.95`) and `status == KEEP`: check whether `score >= threshold`. If yes, stop the loop and notify the user.

### Phase 5: Self-Assessment Survey (MANDATORY)

After every evaluation run, complete the Post-Run Self-Assessment Survey
(`references/memory/post_run_survey.md`). This is how the evaluator itself improves.

**Count-Based Signals**: How many times did you not know what to do next? Use wrong
eval syntax? Miss a required check? Get redirected?

**Qualitative Friction**:
1. Which part of the eval process felt most uncertain or ambiguous?
2. Was any eval prompt poorly scoped (too easy / too adversarial)?
3. What would have made this eval more accurate or useful?
4. What one change to `eval_runner.py` or the evals.json format would help most?

**Improvement Recommendation**: What one change to the eval skill or eval runner
should be tested before the next run? What evidence supports it?

Save to: `temp/retrospectives/survey_[YYYYMMDD]_[HHMM]_os-eval-runner.md`

(`temp/` is the canonical scratch directory for this repo — do not write survey files to the project root or to `context/memory/`.)

---

## The Lab-Space Protocol (Full Lifecycle)

When a skill runs in a **lab repo** (a standalone test repo with copies of plugin files — not the master source), there is a mandatory handoff stage after the loop completes. Lab repos use real file copies; the master repo uses hub-and-spoke symlinks pointing to canonical sources. Changes must be reviewed and backported — never blindly copied.

**Lab runs with `os-eval-runner` installed as a peer:** When the lab repo has both the target skill and `os-eval-runner` installed side by side (the `os-eval-lab-setup` default), the improvement loop will sometimes propose changes to `os-eval-runner` itself — its SKILL.md, eval scripts, or evals. This is expected and productive: the agent finds the highest-leverage change available across all installed skills. The physical copy in the lab is safe to mutate. Treat these changes in backport review with extra scrutiny (see note in Stage 6 below).

### Stage 6: Backport to Master Repo

After the loop completes and the self-assessment survey is written:

**1. Commit and push everything:**
```bash
git add . && git commit -m "post-run: finalize all artifacts"
git push origin main
```

**2. Identify changed files:**
```bash
git log --oneline --name-only  # which commits changed what
git diff <baseline-commit> HEAD --name-only  # all files changed since baseline
```

**3. For each changed file, identify its master source:**

| Component | Skill Installer (Universal) | Claude Code Native |
|:---|:---|:---|
| `<plugin>/skills/<skill>/SKILL.md` | Deployed Skill | `plugins/<plugin>/skills/<skill>/SKILL.md` |
| `<plugin>/skills/<skill>/evals/evals.json` | Deployed Evals | `plugins/<plugin>/skills/<skill>/evals/evals.json` |
| `.agents/skills/os-eval-runner/` (if patched) | Deployed Engine | `plugins/agent-agentic-os/skills/os-eval-runner/` |

**4. For each file — read the diff and assess:**
- **Accept as-is**: change is clearly an improvement, apply verbatim
- **Adapt**: change direction is right but needs adjustment for master context
- **Reject**: change was eval-specific, doesn't generalize, or is a regression

> **Extra scrutiny for `os-eval-runner` changes:** If the loop mutated `eval_runner.py` or `evaluate.py` in the lab, verify the change does not introduce scoring bias that inflates future KEEP rates. The evaluator rewriting its own verdict logic to always exit 0 is the Goodhart failure mode for meta-circular runs. Check the score trajectory in `results.tsv` — a suspiciously high acceptance rate after the change is a red flag.

**5. Apply approved changes deliberately:**
```
# Never blind-copy. Read the diff, understand the intent, edit master files deliberately.
# The master uses symlinks — only update the canonical source file.
```

**6. Two-gate confirmation before applying to master:**

Do not apply any change to master until both gates are cleared:

**Gate 1 — Machine:** `evaluate.py` exited 0 (score ≥ baseline AND f1 ≥ baseline_f1). Confirm from `results.tsv`.

**Gate 2 — Three-perspective diff commentary** (write this before editing master files):
```
BACKPORT REVIEW: iter_NNN — "<desc>"
Score delta: +0.07 (0.82 → 0.89)

Test engineer view:
  Which eval inputs changed verdict? [list them]
  Are these the inputs we were targeting, or collateral?

Routing precision view:
  What similar-but-wrong request could now trigger this skill?

Regression view:
  Do any other installed skills have overlapping keywords with this change?
  grep -r "<new keyword>" .agents/skills/*/SKILL.md
```

For **unattended** (`os-nightly-evolver`) runs: write this commentary to
`temp/retrospectives/backport_[YYYYMMDD]_iter_NNN.md` and flag for human review
before applying. Do not auto-apply to master from unattended runs.

**7. Contribute evolved proposer prompt (if improved during the run):**

If `references/copilot_proposer_prompt.md` was mutated and accepted (KEEPed) during the run,
compare it against the canonical template. If it substantially improved proposal quality, copy it
to the copilot-cli plugin as a reference example:
```bash
cp <lab-experiment-dir>/references/copilot_proposer_prompt.md \
   .agents/skills/copilot-cli-agent/references/skill-proposer-prompt.md
```
This closes the loop: the prompt that emerged from real eval feedback becomes the new starting
baseline for future experiments.

**8. Commit to master:**
```bash
cd <APS_ROOT>
git add plugins/<plugin>/...
git commit -m "backport: <what was accepted from lab run>"
```

> **Trigger the `os-eval-backport` skill** from the master repo session to orchestrate this review. It reads the lab run log, produces a structured diff assessment, and guides the edit.

---

## Troubleshooting

### Exit code reference
| Code | Meaning | Fix |
|:---|:---|:---|
| `0` | KEEP — change accepted | Commit the change |
| `1` | DISCARD — change rejected, auto-reverted | Try a different change |
| `2` | Script error (path, missing file, arg parse) | Check error output; often a template path issue — see below |
| `3` | Locked loop deadlock — environment was tampered after baseline | Delete `<experiment-dir>/evals/.lock.hashes` and re-run `evaluate.py --baseline` |

### Exit 3: tampered environment reset
If you update `evals.json` after a partial baseline run, `evaluate.py` detects the SHA256 mismatch and exits 3. Fix:
```bash
rm <experiment-dir>/evals/.lock.hashes
python3 ./scripts/evaluate.py --skill <experiment-dir> --baseline --desc "re-baseline after evals update"
git add <experiment-dir>/evals/ && git commit -m "baseline: re-baseline after evals update"
```

### Exit 2: standalone template path fail
If `init_autoresearch.py` crashes with a `FileNotFoundError` pointing to a `./` nested path, the script is resolving templates against the full plugin repo layout instead of the installed standalone location. The fix is already applied in the master source (`TEMPLATES_DIR = PLUGIN_ROOT / "assets" / "templates" / "autoresearch"`). If you see it in a locally-patched copy, verify the script's `TEMPLATES_DIR` line uses `HERE.parent` resolution.

### Keywords frontmatter footgun
The `eval_runner.py` scorer treats an explicit `keywords:` field in skill frontmatter as authoritative — it stops scanning the `description` field. If `keywords:` is present but not exhaustive, critical routing words are missed and scores collapse (observed: 1.0000 → 0.5333, F1 1.0 → 0.29 in a single iteration). **Do not add a `keywords:` field unless the list is complete.** Remove it and rely on the description for routing if in doubt.

### 4-character word floor
The scorer only counts words ≥ 4 characters (`\w{4,}`). Words like "fix", "run", "doc" are invisible to the router. Ensure skill descriptions use longer trigger words: "broken", "audit", "paths", "links", "repair", "validation", "commit", "execute", "documentation".

### F1 guard — do not disable
Never disable the `f1 >= baseline_f1` check in `evaluate.py`. It is the only protection against keyword stuffing — where padding the description raises recall at the expense of precision. A high routing accuracy score with low F1 is a red flag, not a victory.

### Structural heuristic penalties
The heuristic engine applies soft penalties for missing structure (e.g. -0.30 for no `<example>` blocks). Do not ignore these even when routing accuracy is high. They are self-correcting signals for documentation quality, not noise.

### .lock.hashes and path portability
`.lock.hashes` currently uses absolute paths. If the skill folder is moved between environments or machines, the baseline hashes will mismatch and trigger exit 3. Re-establish the baseline with `--baseline` after any move.

### Re-baseline required after upgrading evaluate.py or eval_runner.py
Both scripts are SHA256-locked. If you pull an upstream update to either script, existing `.lock.hashes` files will mismatch and trigger exit 3. Fix:
```bash
python3 ./scripts/evaluate.py \
    --skill <experiment-dir> --baseline --desc "re-baseline after script upgrade"
git add <experiment-dir>/evals/ && git commit -m "baseline: re-baseline after evaluate.py upgrade"
```

### Milestone summaries for long runs (25+ iterations)

For runs exceeding 25 iterations, generate a milestone summary to preserve distant history context:

```bash
# Write a milestone if iteration count is a multiple of 25 (auto-check)
python3 ./scripts/generate_milestone.py \
    --experiment-dir <path/to/experiment-dir>

# Force-write a milestone at any iteration count
python3 ./scripts/generate_milestone.py \
    --experiment-dir <path/to/experiment-dir> --force

# Custom interval (e.g. every 10 iterations)
python3 ./scripts/generate_milestone.py \
    --experiment-dir <path/to/experiment-dir> --every 10
```

Output: `evals/traces/milestone_NNN.md` — score trajectory, top KEEPs, worst DISCARDs,
recurring false-positive inputs, dominant problem type, and recommended focus.

The proposer should read milestone summaries for distant history and raw traces for recent
iterations. This prevents the loop from losing context on early experiments as trace count grows.

### Reading traces to diagnose DISCARD iterations
```bash
# Find all false positives across recent traces
grep -h "false positive" evals/traces/iter_*.json | sort | uniq -c | sort -rn

# Show full routing detail for a specific DISCARD
cat evals/traces/iter_002_DISCARD_score0.71.json | python3 -m json.tool

# Show the mutation diff for a DISCARD
python3 -c "import json; d=json.load(open('evals/traces/iter_002_DISCARD_score0.71.json')); print(d['mutation_diff'])"
```

---

## Operating Principles
- **Strict Rigor**: Do not rubber-stamp proposals. If the description is vague, it will over-trigger and break the OS. Fail it.
- **Isolate**: Do not actually write the files. You are an evaluator only. The calling agent is responsible for the final `Write`.
- **Self-Improve**: The survey is not optional. An evaluator that never reflects on its own accuracy is not part of the Triple-Loop.
- **Lab Runs Must Close**: A lab run that ends without a backport review is incomplete. The master source is the only durable artifact.
