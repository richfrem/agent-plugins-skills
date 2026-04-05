# {{SKILL_DISPLAY_NAME}} Eval: Skill Improvement Loop Instructions

<!--
  TEMPLATE — copy this file into your eval test repo and replace all {{PLACEHOLDERS}}:

  {{SKILL_DISPLAY_NAME}}   Human-readable name, e.g. "Link Checker"
  {{SKILL_NAME}}           Skill folder name, e.g. "link-checker-agent"
  {{PLUGIN_DIR}}           Plugin folder name inside test repo, e.g. "link-checker"
  {{MUTATION_TARGET}}      File being optimised, almost always "SKILL.md"
  {{GITHUB_REPO_URL}}      Full HTTPS clone URL, e.g. "https://github.com/richfrem/test-link-checker-eval.git"
  {{ROUND_LABEL}}          Short label for logs/surveys, e.g. "link-checker-round1"
  {{SKILL_EVAL_SOURCE}}    Absolute local path to os-eval-runner skill,
                           e.g. "<SKILL_PATH>/os-eval-runner"
  {{MASTER_PLUGIN_PATH}}   Absolute path to master plugin in agent-plugins-skills,
                           e.g. "<SKILL_PATH>/link-checker"
-->

**Target skill:** `{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/{{MUTATION_TARGET}}`
**Engine:** `os-eval-runner`
**Goal:** Run 10 autonomous optimization iterations on the {{SKILL_NAME}} skill.

---

## ⚠️ Restart Recovery Protocol — Read This First If You Were Just Restarted

If you were restarted mid-run (freeze, context limit, or manual restart), do NOT start over.
Recover state immediately and resume:

1. **Find where you left off:**
   ```bash
   tail -30 temp/logs/run-log_*.md                                        # last logged action
   tail -20 ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/evals/results.tsv     # iteration count + last scores
   git log --oneline -10                                                   # last committed iteration
   git status                                                              # verify clean (no partial edits)
   ```
2. **Verify file state:** If the last iteration was a DISCARD, `evaluate.py` auto-reverted. `git status` should be clean. If a file is modified but uncommitted, read `results.tsv` to determine if it was a pending KEEP or abandoned DISCARD — commit or revert accordingly.
3. **Resume from the next iteration** — do NOT re-run baseline, do NOT re-scaffold. Continue the loop.
4. **Log the restart** in the run log with a `[RESTART]` entry and timestamp before continuing.

**Cold Start (environment wiped — `.lock.hashes` missing):**
If the eval environment was fully reset and `.lock.hashes` is gone, do NOT re-run a fresh baseline — that would overwrite the score history. Instead restore from git:
```bash
# Find the last baseline commit
git log --oneline -- ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/evals/results.tsv | grep -i baseline | head -3

# Restore baseline artifacts from that commit
git checkout <baseline-commit> -- ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/evals/.lock.hashes
git checkout <baseline-commit> -- ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/evals/results.tsv

# Verify restored baseline score
tail -3 ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/evals/results.tsv
```
Resume the loop from the next iteration number. Only re-baseline if the `.lock.hashes` commit cannot be found.

---

## ⚠️ Autonomy Directive — NO INTERRUPTIONS During the Loop

Run the entire improvement loop **without pausing or asking for confirmation**.

- Do NOT ask "Should I proceed?" between iterations
- Do NOT ask for approval before making a change
- Do NOT pause mid-loop to report progress

**NEVER STOP**: Once the loop has begun, do NOT pause to ask the human if you should continue. The human might be asleep or away. You are autonomous. If you run out of ideas, re-read the traces for new angles, try combining previous near-misses, try more targeted description edits. The loop runs until you hit the iteration cap or the human interrupts, period.

The ONLY permitted interruption: a fatal error (Python not found, git not initialized, evaluate.py exit code 2 or 3). For all other cases — including DISCARD verdicts — handle silently and continue.

---

## Step 0: Hardened Repo Bootstrap (Do This First)

0. **Verify Key Variables** (do this before everything else):
   ```bash
   # These should already be substituted by the L0 architect — verify they are correct:
   echo "PLUGIN_DIR = {{PLUGIN_DIR}}"          # should be e.g. mermaid-to-png (NOT 'plugins')
   echo "SKILL_NAME = {{SKILL_NAME}}"          # should be e.g. convert-mermaid
   echo "SKILL_EVAL_SOURCE = {{SKILL_EVAL_SOURCE}}"
   ```
   > ⚠️ If `{{PLUGIN_DIR}}` shows literally `plugins` or is still an unfilled placeholder, STOP.
   > The eval-instructions.md was not correctly filled by the L0 architect. Re-read Step 0 setup instructions.

1. **Set Git Remote** (do this unconditionally — do not ask the user):
   ```bash
   git remote remove origin 2>/dev/null; git remote add origin {{GITHUB_REPO_URL}}
   git remote -v
   ```

2. **Initialize Local Git** (if not already a repo):
   ```bash
   git init && git branch -M main && git add . && git commit -m "init: {{SKILL_NAME}} eval sandbox"
   ```
   > `git branch -M main` ensures the branch is named `main` regardless of the system default (some systems default to `master`), which prevents `git push origin main` from failing later.

3. **Delete Old Config (Clean Slate)**:
   ```bash
   rm -rf .agent .agents .gemini .claude
   ```

4. **Install the Evaluation Engine and Copilot CLI**:
Consult the authoritative installation hub for current deployment commands:

> ### 👉 [INSTALL.md](https://github.com/richfrem/agent-plugins-skills/blob/main/INSTALL.md)

This section ensures the `os-eval-runner` and `copilot-cli-agent` skills are active in your environment.
   > ⚠️ **Known CLI Issues:** The `-y` flag may crash on some versions — if so, run without it and press **Enter** when prompted to accept the default agent list.
   > Both are required: `os-eval-runner` gates iterations, `copilot-cli-agent` proposes mutations.

5. **Verify eval engine scripts are present**:
   ```bash
   ls {{SKILL_EVAL_SOURCE}}/scripts/evaluate.py && echo "engine OK" || echo "MISSING - install os-eval-runner first"
   ls {{SKILL_EVAL_SOURCE}}/scripts/plot_eval_progress.py && echo "plotter OK" || echo "MISSING - copy from APS_ROOT/plugins/agent-agentic-os/scripts/"
   ```

6. **Final Seed & Push**:
   ```bash
   git add . && git commit -m "seed: install os-eval-runner engine"
   git push origin main
   ```

6. **Verify Python 3**:
   ```bash
   python3 --version  # must be 3.8+
   ```

---

## Step 0.4: Functional CLI Heartbeat (Mandatory)

Before establishing the baseline or starting any iterations, you **MUST** verify the Copilot CLI is functional within this lab environment.

```bash
# Run a zero-shot heartbeat test
python3 .agents/skills/copilot-cli-agent/scripts/run_agent.py \
    /dev/null /dev/null ./HEARTBEAT_MD.md \
    "HEARTBEAT CHECK: Respond with 'HEARTBEAT_OK' only."

# Verify and Log
[ -s ./HEARTBEAT_MD.md ] && grep -q "HEARTBEAT_OK" ./HEARTBEAT_MD.md && echo "HEARTBEAT_OK" || (echo "HEARTBEAT_FAIL" && exit 2)
```

**Logging Requirement**: Record the result in your run log (`temp/logs/run-log_*.md`) under the header `## [Step 0.4] [HH:MM] — CLI Heartbeat`. If the test fails, do NOT proceed. Report the failure and halt.

---

## Step 0b: Prepare Test Fixtures

The `test-fixtures/` folder is a **permanent, never-modified** source of test data. Before running any pipeline test, copy it to `working/` at the repo root:

```bash
rm -rf working && cp -r test-fixtures working
```

After each iteration trash and recreate `working/` — never touch `test-fixtures/` itself.

> See `test-fixtures/README.md` for the full expected outcomes table.

---

## Step 0c: Start Run Log

**Create the run log immediately — before doing anything else:**
```bash
mkdir -p temp/logs
```

File: `temp/logs/run-log_[YYYYMMDD]_[HHMM]_{{ROUND_LABEL}}.md`

Log every command, output, error, decision, and result as it happens using this format:

```markdown
## [Step X] [HH:MM] — Short description

**Command / Action:**
<what was run or done>

**Output / Error:**
<paste output verbatim, truncate only if >50 lines>

**Decision:**
<what you decided to do and why>

**Result:**
<what happened next>
```

Log every non-zero exit code, every deviation from instructions, every eval score surprise, every DISCARD and why. **Push the log with every commit.**

> ⚠️ **NEVER delete or compress past entries.** Individual attempt details must be preserved:
> - The exact mutation tried (or a diff)
> - The failure type and which specific eval inputs changed verdict
> - The score delta and why you believe it failed
>
> You MAY append a summary section (e.g. "Round 2 Summary") after a completed round —
> but the individual iteration entries it covers must remain intact beneath it.
> This log is the institutional memory of the experiment. Future sessions use it to avoid
> repeating failed approaches.

---

## Step 1: Scaffold the Experiment

```bash
python3 {{SKILL_EVAL_SOURCE}}/scripts/init_autoresearch.py \
    --experiment-dir ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}} \
    --mutation-target {{MUTATION_TARGET}}
```

> ⚠️ **Standalone Installation Snag:** If this fails with a `FileNotFoundError` or `TemplateNotFound` error referencing a `skills/os-eval-runner/` nested path, the script's `TEMPLATES_DIR` is resolving against the full plugin repo layout instead of the installed location. Patch it:
> ```python
> # In {{SKILL_EVAL_SOURCE}}/scripts/init_autoresearch.py
> # Change TEMPLATES_DIR to use HERE.parent (script-relative resolution):
> HERE = Path(__file__).resolve().parent
> TEMPLATES_DIR = HERE.parent / "assets" / "templates" / "autoresearch"
> ```
> This makes path resolution agnostic to whether the skill is installed standalone or inside the full plugin tree.

This creates:
- `{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/references/program.md`
- `{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/references/copilot_proposer_prompt.md` ← evolvable proposer prompt (read each iteration)
- `{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/evals/evals.json`
- `{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/evals/results.tsv`

---

## Step 2: Customize (Do This Once Before Looping)

Read the skill first:
```bash
cat ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/{{MUTATION_TARGET}}
```

**Edit `references/program.md`**: Fill in the Notes section — what to optimize, target `quality_score` (suggest 0.92), max iterations.

**Edit `evals/evals.json`**: If the file already has well-defined evals, **do not replace them**. If it has `REPLACE` placeholders, fill them in with real test prompts:
- ✅ Positive: prompts that SHOULD trigger this skill
- ❌ Negative: prompts that should NOT trigger this skill

Aim for at least 10 test cases with a good mix. 

**Review Gate:** 
- **Interactive Mode:** Tell the user when ready to review the cases before proceeding.
- **Autonomous Headless Mode:** If you are running headlessly via a CLI orchestrator (e.g. `gemini --yolo --model gemini-3-flash-preview`), do NOT pause. Assume the `evals.json` is sufficient and proceed immediately.
  - **Tool Policy Failures:** If a tool call (like `run_shell_command`) is denied by policy in your headless environment, fallback to using standard bash redirection (`sed`, `cat`, `echo >>`) if possible, or report the failure and continue to the next step.

> ⚠️ **Schema Requirement:** Every test case **must** include a `"should_trigger"` boolean field (`true` or `false`). The eval engine uses this field to calculate accuracy. The legacy `"expected_behavior"` string field is ignored by the scorer and will result in a 0% accuracy baseline.
>
> **Correct schema:**
> ```json
> { "prompt": "...", "should_trigger": true }
> { "prompt": "...", "should_trigger": false }
> ```
> **Wrong (legacy, will break scoring):**
> ```json
> { "prompt": "...", "expected_behavior": "should trigger" }
> ```
>
> ⚠️ **Eval quality — avoid the keyword trap:** The router uses boolean-OR keyword matching.
> Before finalizing your eval suite, check each `should_trigger: true` prompt for "bridge words" —
> words that also appear in `should_trigger: false` prompts. If ALL 4+ char words in a true-positive
> prompt also appear in false-positive prompts, that prompt can never be satisfied without causing a
> false positive. This creates a mathematical ceiling that no description edit can break.
>
> **Fix:** Make adversarial false-positive prompts more conceptual and less keyword-overlapping.
> For example, prefer `"Explain why I would use a git worktree"` over `"What is a git worktree?"`
> — the former shares fewer action-oriented keywords with true-positive prompts.

---

## Step 3: Establish Baseline & Push

```bash
python3 {{SKILL_EVAL_SOURCE}}/scripts/evaluate.py \
    --skill ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}} \
    --baseline \
    --desc "initial baseline"
```

**IMPORTANT — Push the baseline immediately:**
```bash
git add ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/evals/
git commit -m "baseline: initial evaluation snapshot"
git push origin main
```

> Without pushing, the `.lock.hashes` and `results.tsv` won't exist for the next agent session.

---

## Step 4: Run 10 Optimization Iterations (NO INTERRUPTIONS)

**Each iteration follows this exact sequence:**

### Step A: Classify Failure + Check What's Already Been Tried

**A1 — Read current state:**
```bash
tail -5 ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/evals/results.tsv
```
Classify the dominant failure type: `false_positive`, `false_negative`, or `ambiguity`.

**A2 — Read the most recent trace for specifics:**
```bash
ls ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/evals/traces/
cat ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/evals/traces/<latest>.json | python3 -m json.tool
```

**A3 — Scan all traces to avoid repeating a failed mutation (mandatory):**
```bash
for f in ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/evals/traces/iter_*.json; do
  echo "=== $f ===" && python3 -c "import json,sys; d=json.load(open('$f')); print(d.get('mutation_diff','(no diff)'))" 2>/dev/null
done | head -200
```
Before proposing anything, confirm your intended mutation is NOT already in this list.
If it is, pick a different approach — do not re-run a test that already has a trace.

### Step B: Propose Mutation via Copilot CLI

> ⚠️ **MANDATORY**: You MUST run the `copilot` bash command below. Do NOT self-propose.
> Do NOT use the copilot-cli-agent skill. Execute the command and pipe output to disk.

The proposer prompt lives in `references/copilot_proposer_prompt.md` — read it from file each
iteration. Do NOT rebuild the prompt inline. This file is a first-class evolvable artifact.

```bash
# Verify copilot CLI is available
which copilot || (echo "ERROR: copilot CLI not found — halt" && exit 1)

PROMPT_FILE=./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/references/copilot_proposer_prompt.md
[ -f "$PROMPT_FILE" ] || (echo "ERROR: $PROMPT_FILE missing — re-run init_autoresearch.py" && exit 1)

cp ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/{{MUTATION_TARGET}} ./current-skill.md
cp ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/evals/evals.json ./current-evals.json

# Use the Copilot run_agent orchestrator for stable, gpt-5-mini powered mutations
python3 .agents/skills/copilot-cli-agent/scripts/run_agent.py \
  $PROMPT_FILE \
  ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/{{MUTATION_TARGET}} \
  ./proposed-skill.md \
  "Optimize agentic skill routing accuracy. ISSUE: <INSERT_FAILURE_TYPE>. Summary: <INSERT_1_SENTENCE_FAILURE_SUMMARY>"

# Verify non-empty and changed before applying
[ -s ./proposed-skill.md ] || echo "ERROR: empty output — re-prompt with 'try a different approach'"
diff -q ./proposed-skill.md ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/{{MUTATION_TARGET}} > /dev/null && \
  echo "WARNING: identical to current — re-prompt" || \
  cp ./proposed-skill.md ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/{{MUTATION_TARGET}}
```

### Step B.1: Evolve the Proposer Prompt (Second-Order Mutation)

After **3 consecutive DISCARDs** with the same failure type, the prompt itself may be the
bottleneck — not the skill. Try one focused edit to `references/copilot_proposer_prompt.md`:
- Add a clarifying constraint that addresses the recurring failure pattern
- Sharpen the strategy section with the specific word-overlap insight from the traces
- Adjust the output format if the CLI is returning commentary or fences

Gate it the same way: edit → eval → KEEP or revert. Log it as "prompt evolution" in the run log.

Other second-order mutations if the loop stalls for 5+ consecutive DISCARDs:
- **`references/program.md`** — clarify the goal or locked-files list if it has become ambiguous
- **`copilot-cli-agent/SKILL.md`** — if the proposer skill description is missing patterns you rely on

### Step B.2: Creativity Unblocking (when out of ideas)

If you have exhausted obvious mutation angles and DISCARDs keep repeating, try these before
giving up:

**Option 1 — Web research:**
Use your web search tool to find real-world context for the skill's domain. Search for:
- How users actually phrase requests for this capability (forum posts, docs, issue titles)
- Related tools or concepts that share vocabulary with the skill
- Common synonyms or alternative framings you haven't tried

Extract candidate trigger words from what you find, cross-check them against `evals.json`
for overlap risk, then incorporate the most distinctive ones into the next mutation.

> **Note:** Synonym hunting often fails for action-oriented skills — real-world docs tend to
> use the same trapped keywords. If web research yields nothing distinctive, pivot to
> **Negative Exclusion**: run the collision matrix (Step A3) and focus on *removing* bridge
> words from the description rather than adding new trigger words.

**Option 2 — Ask Copilot for strategy ideas (not a mutation):**
Use Copilot as a brainstorm partner — ask for *approaches to try*, not a rewrite:
```bash
# Use the Copilot run_agent orchestrator for gpt-5-mini strategy brainstorming
python3 .agents/skills/copilot-cli-agent/scripts/run_agent.py \
  /dev/null /dev/null ./strategy-ideas.md \
  "I am optimizing a Claude Code SKILL.md routing description using a TF-IDF
keyword scorer (4+ char words, exact match only, no semantics).
Current score: <score>. Stuck on this failure: <failure_type> — <summary>.
Strategies already tried: <list briefly>.
Suggest 3 distinct strategies I haven't tried yet. Do NOT rewrite the skill.
Output a numbered list of strategy ideas only."
cat ./strategy-ideas.md
```
Read the ideas, pick the most promising one, then run the normal Step B mutation call
with that strategy embedded in the failure analysis line.

Log both options in the run log under `[CREATIVITY UNBLOCK]` before proceeding.

### Step C: Eval Gate
```bash
python3 {{SKILL_EVAL_SOURCE}}/scripts/evaluate.py \
    --skill ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}} \
    --desc "description of what changed"
```

- `exit 0` (KEEP) → `git add . && git commit -m "keep: <desc>" && git push origin main`
- `exit 1` (DISCARD) → already auto-reverted, move to next iteration silently

Repeat for **10 total iterations** — no check-ins, no user confirmation.

### Step 5: Iteration Visibility Sync (Scoreboard)

After every iteration (KEEP or DISCARD), you MUST update the markdown progress table in `./LOG_PROGRESS.md`:

```bash
# Initialize scoreboard if missing
[ -f ./LOG_PROGRESS.md ] || echo "| Iteration | Score | Verdict | Reason |" > ./LOG_PROGRESS.md
[ -f ./LOG_PROGRESS.md ] || echo "|:---|:---|:---|:---|" >> ./LOG_PROGRESS.md

# Append the latest result from results.tsv
SCORE=$(tail -1 ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/evals/results.tsv | cut -f2)
VERDICT=$(tail -1 ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/evals/results.tsv | cut -f4)
REASON=$(tail -1 ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/evals/results.tsv | cut -f5)
ITERATION_NUM=$(tail -1 ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/evals/results.tsv | cut -f1)
echo "| $ITERATION_NUM | $SCORE | $VERDICT | $REASON |" >> ./LOG_PROGRESS.md
```

---

## Step 5: Generate Progress Plot and Self-Assessment Survey

After all 10 iterations:

1. **Plot the Score Progress:**
```bash
python3 {{SKILL_EVAL_SOURCE}}/scripts/plot_eval_progress.py \
    --tsv ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/evals/results.tsv \
    --out ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/evals/eval_progress.png
```
(*Commit the `eval_progress.png` image directly to the repo so it's backed up.*)

2. **Write your post-run self-assessment to:**
```
temp/retrospectives/survey_[YYYYMMDD]_[HHMM]_{{ROUND_LABEL}}.md
```

---

## Step 6: Handoff to Master Repo

**This repo contains COPIES of the master plugin files.** Improvements here must be reviewed and backported manually to:
```
{{MASTER_PLUGIN_PATH}}
```

**Backport Package — what to include vs exclude:**

| Include | Exclude |
|:---|:---|
| Final `{{MUTATION_TARGET}}` (if improved) | `evals/results.tsv` (experiment ledger) |
| Evolved `references/copilot_proposer_prompt.md` (if substantially improved) | `evals/traces/` (per-iteration diagnostics) |
| `references/program.md` (if goal/notes are useful to future runs) | `evals/.lock.hashes` (environment-specific) |
| Self-assessment survey | Round-specific log files |

After the run, the reviewing agent will:
1. Read your run log and self-assessment
2. Check which files changed: `git log --name-only` and `git diff <baseline-commit> HEAD`
3. Assess each change and apply approved ones to the master plugin sources

**Your job:** ensure everything is committed and pushed to `{{GITHUB_REPO_URL}}` so the full history is visible for review.

---

## Validation Checklist

- [ ] Git remote set to `{{GITHUB_REPO_URL}}`
- [ ] Run log created at step 0 and pushed with every commit
- [ ] Test fixtures copied to `working/` before pipeline runs
- [ ] Baseline established and pushed
- [ ] One focused change per iteration (no bulk rewrites)
- [ ] Each KEEP committed; each DISCARD auto-reverted
- [ ] `git push origin main` completed after loop
- [ ] Self-assessment survey written
- [ ] Handoff section reviewed — master repo paths noted for backport
