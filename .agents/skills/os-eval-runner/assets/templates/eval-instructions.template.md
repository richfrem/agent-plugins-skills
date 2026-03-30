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
                           e.g. "/Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/agent-agentic-os/skills/os-eval-runner"
  {{MASTER_PLUGIN_PATH}}   Absolute path to master plugin in agent-plugins-skills,
                           e.g. "/Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/link-checker"
-->

**Target skill:** `{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/{{MUTATION_TARGET}}`
**Engine:** `os-eval-runner`
**Goal:** Run 10 autonomous optimization iterations on the {{SKILL_NAME}} skill.

---

## Step 0: Hardened Repo Bootstrap (Do This First)

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

4. **Install the Evaluation Engine**:
   ```bash
   npx skills add -y {{SKILL_EVAL_SOURCE}}
   ```
   > ⚠️ **Known CLI Issues:** The `-y` flag may crash on some versions — if so, run without it and press **Enter** when prompted to accept the default agent list.

5. **Final Seed & Push**:
   ```bash
   git add . && git commit -m "seed: install os-eval-runner engine"
   git push origin main
   ```

6. **Verify Python 3**:
   ```bash
   python3 --version  # must be 3.8+
   ```

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

---

## Step 1: Scaffold the Experiment

```bash
python3 .agents/skills/os-eval-runner/scripts/init_autoresearch.py \
    --experiment-dir ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}} \
    --mutation-target {{MUTATION_TARGET}}
```

> ⚠️ **Standalone Installation Snag:** If this fails with a `FileNotFoundError` or `TemplateNotFound` error referencing a `skills/os-eval-runner/` nested path, the script's `TEMPLATES_DIR` is resolving against the full plugin repo layout instead of the installed location. Patch it:
> ```python
> # In .agents/skills/os-eval-runner/scripts/init_autoresearch.py
> # Change TEMPLATES_DIR to use HERE.parent (script-relative resolution):
> HERE = Path(__file__).resolve().parent
> TEMPLATES_DIR = HERE.parent / "assets" / "templates" / "autoresearch"
> ```
> This makes path resolution agnostic to whether the skill is installed standalone or inside the full plugin tree.

This creates:
- `{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/references/program.md`
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

Aim for at least 10 test cases with a good mix. **Tell the user when ready to review before proceeding.**

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

---

## Step 3: Establish Baseline & Push

```bash
python3 .agents/skills/os-eval-runner/scripts/evaluate.py \
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

## Step 4: Run 10 Optimization Iterations

1. Make **one focused change** to `./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}}/{{MUTATION_TARGET}}`
2. Run the scorer:
   ```bash
   python3 .agents/skills/os-eval-runner/scripts/evaluate.py \
       --skill ./{{PLUGIN_DIR}}/skills/{{SKILL_NAME}} \
       --desc "description of what you changed"
   ```
3. `exit 0` (KEEP) → `git add . && git commit -m "keep: <desc>"`
4. `exit 1` (DISCARD) → already auto-reverted, try a different change
5. Repeat for **10 total iterations**
6. **Push when done**: `git push origin main`

---

## Step 5: Self-Assessment Survey

After all 10 iterations, write your post-run self-assessment to:
```
temp/retrospectives/survey_[YYYYMMDD]_[HHMM]_{{ROUND_LABEL}}.md
```

---

## Step 6: Handoff to Master Repo

**This repo contains COPIES of the master plugin files.** Improvements here must be reviewed and backported manually to:
```
{{MASTER_PLUGIN_PATH}}
```

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
