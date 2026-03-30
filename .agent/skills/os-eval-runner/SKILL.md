---
name: os-eval-runner
description: >
  Trigger with "evaluate this skill", "run the autoresearch loop on", "run tests on the new skill",
  "check if this change breaks anything", "evaluate the learning loop proposal",
  "measure the performance gain", "optimize this skill", "improve this skill autonomously",
  or when an agent (like `os-learning-loop`) proposes a change to an existing skill and needs
  empirical validation before writing it to disk.

  <example>
  Context: User wants to start an autonomous improvement loop on a skill.
  user: "Run the autoresearch loop on plugins/agent-agentic-os/skills/os-health-check for 20 iterations"
  assistant: [triggers os-eval-runner, runs Phase 0 intake to confirm target, metrics, and iteration cap]
  <commentary>
  Explicit loop request with target path and iteration count — go straight to intake confirmation then Mode 1.
  </commentary>
  </example>

  <example>
  Context: User wants to optimize a skill but hasn't specified details.
  user: "Optimize the commit skill"
  assistant: [triggers os-eval-runner, runs Phase 0 intake interview to gather target path, mode, metrics, iterations]
  <commentary>
  Incomplete request — run the intake interview before starting any loop.
  </commentary>
  </example>

  <example>
  Context: `os-learning-loop` has a proposed skill edit and needs validation before writing.
  assistant: [autonomously] "Before I apply this description change to os-memory-manager, I'll run os-eval-runner to confirm routing accuracy doesn't regress."
  <commentary>
  Implicit audit trigger -- agent self-gates on the evaluator before any skill write. Mode 2 single-shot QA.
  </commentary>
  </example>

  <example>
  Context: An agent is asking for general information about a skill, not evaluating a proposed change.
  agentic-os-setup: "Tell me about the os-clean-locks skill."
  assistant: "It cleans up stale lock files..."
  <commentary>
  Information request, not an evaluation trigger. Do not trigger os-eval-runner.
  </commentary>
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
  assets/templates/autoresearch/               <-- TEMPLATES (master copies, never edit directly)
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
```

## Setup: Start a New Experiment (4 steps)

**Step 0 — Hardened Bootstrap (Fresh Repo Only):**
Before running any loops in a new environment, ensure it is clean and correctly linked:
1. **Check Git Remote**: `git remote -v`. If blank, ask the user for the repo URL.
2. **Initialize Local Git**: `git init && git add . && git commit -m "init"`.
3. **Delete Old Config**: `rm -rf .agent .agents .gemini .claude`.
4. **Install Skill via Full Path**: `npx skills add -y <YOUR CLONED REPO PATH>/plugins/agent-agentic-os/skills/os-eval-runner`.
5. **Verify Python 3**: `python3 --version` (must be 3.8+).

**Step 1 — Deploy templates into your experiment directory:**
```bash
python3 plugins/agent-agentic-os/scripts/init_autoresearch.py \
    --experiment-dir <path/to/your-experiment-dir> \
    --mutation-target SKILL.md   # or any filename being mutated
```
This creates `references/program.md`, `evals/evals.json`, and `evals/results.tsv` in your experiment dir. Templates stay untouched.

**Step 2 — Edit the deployed files:**
- `references/program.md` — fill in the Notes section: what are you optimizing, target score, max iterations
- `evals/evals.json` — replace the `REPLACE` placeholders with real test inputs and `should_trigger` values

**Step 3 — Establish baseline and start the loop:**
```bash
python3 plugins/agent-agentic-os/scripts/evaluate.py \
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
| Scoring scripts | `plugins/agent-agentic-os/scripts/evaluate.py`, `eval_runner.py` |
| Scaffold script | `plugins/agent-agentic-os/scripts/init_autoresearch.py` |
| program.md **template** | `skills/os-eval-runner/assets/templates/autoresearch/program.md.template` |
| evals.json **template** | `skills/os-eval-runner/assets/templates/autoresearch/evals.json.template` |
| results.tsv **template** | `skills/os-eval-runner/assets/templates/autoresearch/results.tsv.template` |

### What lives with the target (deployed per experiment, most appropriate location)

The mutation target can be a SKILL.md, a Python script, a config file, or anything
with a clear metric. All experiment state deploys alongside the target — not here.

| What | Location |
|---|---|
| program.md (rendered from template) | `<experiment-dir>/references/program.md` |
| evals.json (rendered from template) | `<experiment-dir>/evals/evals.json` |
| results.tsv (loop ledger) | `<experiment-dir>/evals/results.tsv` |
| .lock.hashes (SHA256 snapshot) | `<experiment-dir>/evals/.lock.hashes` |

Where `<experiment-dir>` is the directory most natural to the target:
- Evaluating a skill → the skill's own directory (e.g. `plugins/my-plugin/skills/my-skill/`)
- Evaluating a Python module → the module's project directory
- Evaluating a config or model → wherever that experiment lives

**Deploy the templates to a new experiment:**
```bash
python plugins/agent-agentic-os/scripts/init_autoresearch.py \
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
  Run: `python3 plugins/agent-agentic-os/scripts/init_autoresearch.py --experiment-dir <experiment-dir> --mutation-target <filename>`
  Then pause for the user to fill in the test cases.

**Q6 — (Loop mode only) Does `program.md` exist?**
Check `<experiment-dir>/references/program.md`.
- If exists: read it and show the goal. Confirm it still reflects what the user wants to optimize.
- If missing: "No program.md found. I'll scaffold it from the standard template:"
  ```bash
  python plugins/agent-agentic-os/scripts/init_autoresearch.py \
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
1. Read `<target-skill>/references/program.md` (goal + locked files + NEVER STOP). If missing, run `python3 plugins/agent-agentic-os/scripts/init_autoresearch.py --skill <target-path>` first.
2. Establish a baseline if none exists: `python3 plugins/agent-agentic-os/scripts/evaluate.py --skill <path/to/skill-folder> --baseline`
3. Loop N times (default: run until told to stop per NEVER STOP directive):
   - Make one focused change to `SKILL.md`
   - Run `python3 scripts/evaluate.py --skill <path/to/skill-folder> --desc "what changed"`
   - exit 0 (KEEP): `git add SKILL.md && git commit -m "keep: score=X <desc>"`
   - exit 1 (DISCARD): `git checkout -- <path>/SKILL.md`

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
python3 scripts/evaluate.py --skill path/to/skill-folder --desc "what changed"
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
(`references/post_run_survey.md`). This is how the evaluator itself improves.

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

| Lab file | Master source in `agent-plugins-skills` |
|:---|:---|
| `<plugin>/skills/<skill>/SKILL.md` | `plugins/<plugin>/skills/<skill>/SKILL.md` |
| `<plugin>/skills/<skill>/evals/evals.json` | `plugins/<plugin>/skills/<skill>/evals/evals.json` |
| `.agents/skills/os-eval-runner/` (if patched) | `plugins/agent-agentic-os/skills/os-eval-runner/` |

**4. For each file — read the diff and assess:**
- **Accept as-is**: change is clearly an improvement, apply verbatim
- **Adapt**: change direction is right but needs adjustment for master context
- **Reject**: change was eval-specific, doesn't generalize, or is a regression

**5. Apply approved changes deliberately:**
```
# Never blind-copy. Read the diff, understand the intent, edit master files deliberately.
# The master uses symlinks — only update the canonical source file.
```

**6. Commit to master:**
```bash
cd /path/to/agent-plugins-skills
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
python3 scripts/evaluate.py --skill <experiment-dir> --baseline --desc "re-baseline after evals update"
git add <experiment-dir>/evals/ && git commit -m "baseline: re-baseline after evals update"
```

### Exit 2: standalone template path fail
If `init_autoresearch.py` crashes with a `FileNotFoundError` pointing to a `skills/os-eval-runner/` nested path, the script is resolving templates against the full plugin repo layout instead of the installed standalone location. The fix is already applied in the master source (`TEMPLATES_DIR = PLUGIN_ROOT / "assets" / "templates" / "autoresearch"`). If you see it in a locally-patched copy, verify the script's `TEMPLATES_DIR` line uses `HERE.parent` resolution.

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

---

## Operating Principles
- **Strict Rigor**: Do not rubber-stamp proposals. If the description is vague, it will over-trigger and break the OS. Fail it.
- **Isolate**: Do not actually write the files. You are an evaluator only. The calling agent is responsible for the final `Write`.
- **Self-Improve**: The survey is not optional. An evaluator that never reflects on its own accuracy is not part of the flywheel.
- **Lab Runs Must Close**: A lab run that ends without a backport review is incomplete. The master source is the only durable artifact.
