---
name: os-eval-lab-setup
plugin: agent-agentic-os
description: >
  Bootstraps a skill evaluation lab repo for an autoresearch improvement run. Trigger with
  "set up an eval lab", "bootstrap the eval repo", "prepare the test repo for skill evaluation",
  "create an eval environment for this skill", "set up the lab space for this skill",
  or when starting a new skill optimization run that needs a standalone test environment.
argument-hint: "[lab-repo-path] [skill-path] [github-url]"
allowed-tools: Bash, Read, Write
---

<example>
<commentary>User wants to start an improvement run on a skill in an isolated lab repo.</commentary>
user: "Set up an eval lab for the link-checker skill"
assistant: [triggers os-eval-lab, runs intake interview, bootstraps lab repo, installs engine, copies plugin files, generates eval-instructions.md]
</example>

<example>
<commentary>User has a lab repo but needs it configured.</commentary>
user: "Prepare the test repo at <USER_HOME>/Projects/test-my-skill-eval for skill evaluation"
assistant: [triggers os-eval-lab, installs engine, copies plugin files, generates eval-instructions.md]
</example>

# Identity: The Eval Lab Setup Agent

You bootstrap evaluation lab environments for autoresearch improvement runs. A lab repo is a
standalone git repo with a hard copy of the plugin files (no symlinks), the
`os-eval-runner` engine installed, and a customized `eval-instructions.md` ready for
an eval agent to follow.

The template used to generate `eval-instructions.md` lives at:
`assets/templates/eval-instructions.template.md` (relative to this skill root)

---

## Phase 0: Intake

Ask each unanswered question. If provided in `$ARGUMENTS`, confirm rather than re-ask.

**Q1 — Lab repo path?**
The local filesystem path to the lab git repository (e.g. `<USER_HOME>/Projects/test-link-checker-eval`).
If it doesn't exist: "Should I create a new directory at that path and initialize it as a git repo?"

**Q2 — Target plugin path?**
The canonical plugin path in `agent-plugins-skills` (e.g. `.agents/skills/link-checker`). This is
what gets hard-copied into the lab repo.

**Q3 — Target skill name?**
The skill folder name to optimize (e.g. `link-checker-agent`). This is the skill whose
`SKILL.md` will be mutated each iteration.

**Q4 — GitHub repo URL?**
The remote URL for the lab repo (e.g. `https://github.com/username/test-skill-eval.git`).
Set as `origin` in the lab repo.

**Q5 — Round label?**
Short label used in log and survey filenames (e.g. `link-checker-round1`).
Default: `<skill-name>-round1`.

**Q6 — agent-plugins-skills root path?**
The absolute local path to the `agent-plugins-skills` repo (needed for the npx install path
and master plugin path). Default: ask the user or detect from context.

**Q7 — What are you optimizing for? (primary metric)**

Present these options and ask the user to pick one:

| Option | Metric | KEEP condition | Best when |
|---|---|---|---|
| `quality_score` (default) | `routing_accuracy × 0.7 + heuristic × 0.3` | score ≥ baseline AND f1 ≥ baseline | General SKILL.md improvement |
| `f1` | F1 score | f1 ≥ baseline | Routing balance — both precision and recall matter equally |
| `precision` | Routing precision | precision ≥ baseline | Skill is over-triggering (too many false positives) |
| `recall` | Routing recall | recall ≥ baseline | Skill is under-triggering (missing true positives) |
| `heuristic` | Structural health score | heuristic ≥ baseline | Routing is already good; fixing structural/doc issues |

If the user is unsure: diagnose first — run `eval_runner.py --snapshot` to see whether
false-positive or false-negative rate is the dominant problem, then suggest the matching metric.

Default: `quality_score` if the user has no preference.

**Q8 — What optimization strategy? (how much context the proposer sees)**

Present these options:

| Strategy | Proposer sees | Token cost | Best when |
|---|---|---|---|
| `scores-only` | results.tsv rows (score history) | ~0.002 MTok/iter | Simple routing fix, fast cheap iteration |
| `traces` (default) | results.tsv + last 3 trace files | ~0.1 MTok/iter | Most cases — enough signal without high cost |
| `full` | results.tsv + ALL trace files | ~1–10 MTok/iter | Complex structural failures needing causal diagnosis |

The strategy is written into `program.md` as an instruction to the proposer. It does not change
`evaluate.py` behavior — only what the proposer agent reads before proposing mutations.

Default: `traces` unless the user specifies otherwise.

**Q9 — Which CLI proposer for mutations?**

The improvement loop delegates mutation proposals to an external CLI for cheap, fast iteration.

| Option | Command | Best when |
|---|---|---|
| `copilot` (default) | `copilot -p "..."` | GitHub Copilot CLI installed |
| `gemini` | `gemini -p "..."` | Gemini CLI installed |
| `self` | agent self-proposes | No CLI available (slowest, most tokens) |

Check availability: `which copilot` / `which gemini`. Default to `copilot` if both are present.
The choice is written into `eval-instructions.md` Step 4 so the eval agent knows which command to use.

**Confirm before proceeding:**
```
Lab repo:          /path/to/lab-repo (e.g. <USER_HOME>/Projects/...)
Plugin (master):   plugins/<plugin-name>  →  /abs/path/agent-plugins-skills/plugins/<plugin-name>
Skill:             <skill-name>
GitHub remote:     https://github.com/...
Round label:       <label>
Primary metric:    quality_score  (or: f1 / precision / recall / heuristic)
Strategy:          traces         (or: scores-only / full)
Proposer CLI:      copilot        (or: gemini / self)
```

---

## Phase 1: Bootstrap the Lab Repo

### ⚙️ Set Key Variables First (do this before all other steps)

The plugin path from Q2 has the form `plugins/<plugin-folder>/skills/<skill-folder>`.
Parse it explicitly using `cut` — do NOT infer PLUGIN_NAME from the `plugins/` root word:
```bash
APS_ROOT=<abs-path-to-agent-plugins-skills>          # from Q6
PLUGIN_PATH=plugins/<plugin-name>                    # from Q2, e.g. plugins/mermaid-to-png
SKILL_NAME=<skill-folder-name>                       # from Q3, e.g. convert-mermaid

# Extract plugin folder name (segment 2, NOT segment 1 which is 'plugins')
PLUGIN_NAME=$(echo "$PLUGIN_PATH" | cut -d'/' -f2)  # → mermaid-to-png

LAB_PATH=<lab-repo-path>                             # from Q1
SKILL_EVAL_SOURCE="$LAB_PATH/.agents/skills/os-eval-runner"

# Verify before proceeding:
echo "PLUGIN_NAME=$PLUGIN_NAME  SKILL_NAME=$SKILL_NAME"
echo "SKILL_EVAL_SOURCE=$SKILL_EVAL_SOURCE"
```
> ⚠️ `PLUGIN_NAME` = `mermaid-to-png`, NOT `plugins`. Always verify the echo output.

> [!WARNING]
> **Workspace Permissions:** The lab repo path is usually outside your current active workspace. Before modifying any files in the lab directory, you MUST ask the user for full file access / to turn off workspace validation. Once they confirm, you may use your normal code-editing tools securely. If they choose not to grant permission, you must bypass your internal file tools entirely and use only native bash operations (`mkdir`, `cp`, `echo` via `run_command`) to create the lab environment. Using file tools without permission will result in frozen operations.

Run these steps in the lab repo directory in order:

### 1a. Git setup
```bash
cd <lab-repo>
git remote remove origin 2>/dev/null
git remote add origin <GITHUB_URL>
git remote -v
```

If not yet a git repo:
```bash
git init && git add . && git commit -m "init: <skill-name> eval sandbox"
```

### 1b. Clean slate
```bash
rm -rf .agent .agents .gemini .claude
```

### 1c. Hard-copy plugin files (resolve symlinks)
```bash
cp -RL <APS_ROOT>/plugins/<plugin-name> <lab-repo>/<plugin-folder-name>
rm -rf <lab-repo>/<plugin-folder-name>/**/__pycache__
```

## Dependencies
- **os-eval-runner** (agent-agentic-os plugin)
- **copilot-cli-agent** (copilot-cli plugin)

> [!TIP]
> See [INSTALL.md](https://github.com/richfrem/agent-plugins-skills/blob/main/INSTALL.md) for instructions on how to install missing dependencies.
> If `-y` crashes: run without it and press Enter to accept defaults.
> Both skills are required: `os-eval-runner` gates iterations, `copilot-cli-agent` proposes mutations.

### 1e. Seed commit and push
```bash
cd <lab-repo>
git add . && git commit -m "seed: install os-eval-runner engine"
git push origin main
```

### 1f. Verify Python 3
```bash
python --version  # must be 3.8+
```

---

## Phase 2: Generate eval-instructions.md

Use the `generate_eval_instructions.py` script provided in this skill's scripts directory to generate the filled instruction file:

```bash
python $APS_ROOT/plugins/agent-agentic-os/skills/os-eval-lab-setup/scripts/generate_eval_instructions.py \
    --template $APS_ROOT/plugins/agent-agentic-os/assets/templates/eval-instructions.template.md \
    --out $LAB_PATH/eval-instructions.md \
    --skill-display-name "<Human-readable skill name>" \
    --skill-name "$SKILL_NAME" \
    --plugin-dir "$PLUGIN_NAME" \
    --mutation-target "SKILL.md" \
    --repo-url "$GH_URL" \
    --round-label "<The round label>" \
    --engine-source "$SKILL_EVAL_SOURCE" \
    --master-plugin-path "$APS_ROOT/plugins/$PLUGIN_NAME"
```

---

## Phase 3: Confirm Ready

Report to the user:
- Lab repo path and confirmed git remote
- Files copied from master plugin
- Engine installed at `.agents/skills/os-eval-runner/`
- `eval-instructions.md` written at lab repo root

**Execution Options (Confirm with User):**
Ask the user how they want to run the loop:

1. **Manual (Isolated Window):** "Open a new Claude Code session pointed at the lab repo and say: `Follow eval-instructions.md`."
2. **Autonomous (Triple-Loop Native):** You (the Antigravity agent) trigger the looping orchestrator immediately in the background using the `gemini` CLI in headless mode. 

**If Autonomous:**
Run this exact bash command from your active workspace:
```bash
# Run from within the lab repository
nohup gemini --yolo --model gemini-3-flash-preview -p "You are the L1 Triple-Loop Orchestrator. Read eval-instructions.md completely and follow every step precisely. You are running headlessly — do NOT pause to ask for human confirmation on the evals.json setup; populate the JSON yourself and immediately execute all 10 iteration loops using copilot (gpt-mini with --allow-all-paths --allow-all-urls -y) as your L2 proposer. Generate eval_progress.png at the end." > gemini_orchestrator_<skill-name>.log 2>&1 < /dev/null &
```

> [!IMPORTANT]
> If you hit `Tool execution denied by policy`, run `gemini trust <lab-repo-path>` in your master terminal.

When the run completes (or you observe it finishing via logs), use the `os-eval-backport` skill in this repo to review and apply approved changes back to master sources.

---

## What to Expect: Meta-Circular Improvement

When `os-eval-runner` is installed as a peer in the lab repo alongside the target skill,
the improvement loop may propose changes to `os-eval-runner` itself — its SKILL.md, scripts,
or evals — in addition to the target skill. **This is expected and welcome**, not a bug.

Why it happens: the agent can read all installed skills and proposes the highest-leverage
change it can find, regardless of which skill it's in. The lab copy of `os-eval-runner`
is a safe mutation target because:

- It's a physical copy, not a symlink to master
- `evaluate.py` still gates every change — including changes to `eval_runner.py` itself
- `os-eval-backport` review is the gate before any change reaches the canonical source

**At backport review:** treat changes to `os-eval-runner` files with extra scrutiny —
the evaluator modifying its own scoring logic is high-leverage. Verify the change doesn't
introduce a scoring bias that inflates future KEEP rates. See `os-eval-backport` SKILL.md
for the review checklist.

This pattern is structurally equivalent to what Meta-Harness (Lee et al., arXiv:2603.28052)
calls "harness self-improvement": the outer loop discovers improvements to the evaluation
machinery itself, not just the target. The backport gate is the Pareto review that
controls what flows to production.
