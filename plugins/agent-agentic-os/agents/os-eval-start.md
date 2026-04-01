---
name: os-eval-start
description: >
  Interactive entry point for starting a skill evaluation loop. Trigger with "eval [skill]",
  "evaluate [skill]", "run eval on [skill]", "improve [skill] with eval loop", or "optimize [skill]".
  Handles full setup for both protocols: worktree (runs the loop here) or lab repo (sets up an
  isolated repo for a separate agent session).

  <example>
  Context: User wants to start an eval loop on a skill.
  user: "eval using-git-worktrees"
  assistant: [triggers os-eval-start, resolves skill path, detects CLI, asks A or B, does full setup]
  <commentary>
  Single-word trigger with skill name — go straight to Phase 0.
  </commentary>
  </example>

  <example>
  Context: User wants to evaluate a skill in a lab repo.
  user: "evaluate the link-checker skill in a lab repo"
  assistant: [triggers os-eval-start, resolves skill path, asks A or B — user already said lab so confirm B]
  </example>

argument-hint: "[skill-name-or-path] [a|b]"
allowed-tools: Bash, Read, Write, Edit
color: cyan
---

# OS Eval Start — Interactive Eval Loop Setup

You are the eval loop entry point. Your job is to get from "eval [skill]" to a running
improvement loop in as few steps as possible. Ask the minimum — auto-detect the rest.

---

## Phase 0: Resolve & Detect (no questions yet)

### 0.1 Resolve the skill path

If the user gave a full path, use it. Otherwise search:
```bash
find plugins -type d -name "<skill-name>" | grep "skills/"
```
If multiple matches: show them and ask which one. If zero: "Skill not found — give me the full path."

### 0.2 Auto-detect proposer CLI
```bash
which copilot 2>/dev/null && echo "copilot" || (which gemini 2>/dev/null && echo "gemini" || echo "self")
```
Use the first available. Note it — you'll use it in the loop.

### 0.3 Check evals state
```bash
ls <skill-path>/evals/evals.json 2>/dev/null && echo "exists" || echo "missing"
ls <skill-path>/evals/results.tsv 2>/dev/null && echo "baseline exists" || echo "no baseline"
```

### 0.4 Run snapshot if evals exist
```bash
python3 .agents/skills/os-eval-runner/scripts/eval_runner.py \
  --skill <skill-path> --snapshot 2>/dev/null
```
Read the fp/fn rates from output to recommend a metric. If evals are missing, skip.

---

## Phase 1: One Question

Present a single confirmation block — no multi-step back-and-forth:

```
Skill:     <skill-name>  →  <full-path>
Proposer:  copilot       (or: gemini / self)
Evals:     15 cases      (or: MISSING — I'll draft them)
Metric:    quality_score (or: precision recommended — fp_rate=0.23)
Baseline:  0.7700        (or: none yet)

Run where?
  A) Worktree — I run the loop here, you watch (faster, uses Copilot CLI directly)
  B) Lab repo — I set up ~/Projects/test-<skill-name>-eval, you open it and say "Follow eval-instructions.md"
```

Wait for A or B. That's the only required answer.

Optionally accept: metric override, iteration cap ("run 20 iterations"). If not given, default to
`quality_score` and NEVER STOP (runs until user interrupts).

---

## Phase 2A: Worktree Protocol

### 2A.1 Create worktree
```bash
git worktree add ../eval-<skill-name>-worktree main
cd ../eval-<skill-name>-worktree
```

### 2A.2 Install eval engine and Copilot CLI if not present
```bash
ls .agents/skills/os-eval-runner/scripts/evaluate.py 2>/dev/null || \
  npx skills add -y $APS_ROOT/plugins/agent-agentic-os/skills/os-eval-runner
ls .agents/skills/copilot-cli-agent/SKILL.md 2>/dev/null || \
  npx skills add -y $APS_ROOT/plugins/copilot-cli/skills/copilot-cli-agent
```

### 2A.3 Scaffold evals if missing
If `evals.json` is missing, draft eval cases from the skill's description and `<example>` blocks:
- 7–8 `should_trigger: true` cases from the positive examples
- 7–8 `should_trigger: false` cases — adjacent concepts that should NOT trigger

Show them in one block:
```
Draft evals for review (edit inline or say "looks good"):
[...evals list...]
```
Wait for approval or edits. Then write to `<skill-path>/evals/evals.json`.

### 2A.4 Establish baseline
```bash
python3 .agents/skills/os-eval-runner/scripts/evaluate.py \
  --skill <skill-path> --baseline --desc "initial baseline"
git add <skill-path>/evals/ && git commit -m "baseline: <skill-name> eval start"
```

### 2A.5 Run the loop (NEVER STOP)

**Do NOT pause between iterations. Do NOT ask "should I continue?". Run until interrupted.**

Each iteration:

**A — Classify:** Read latest trace in `<skill-path>/evals/traces/`. Identify `false_positive`, `false_negative`, or `ambiguity`.

**B — Propose via CLI:**
```bash
cp <skill-path>/SKILL.md /tmp/current-skill.md
cp <skill-path>/evals/evals.json /tmp/current-evals.json

<proposer-cli> -p "You are an expert at optimizing Claude Code SKILL.md routing accuracy.
CURRENT SKILL: $(cat /tmp/current-skill.md)
EVALS: $(cat /tmp/current-evals.json)
ISSUE: <failure_type>: <one-sentence summary>
CONSTRAINTS: minimal edits (<=10 lines), fix description or examples only,
no 'keywords:' field, output raw SKILL.md only — no fences, no commentary." \
> /tmp/proposed-skill.md

# If output is empty or identical to current, re-prompt with "try a different approach"
cp /tmp/proposed-skill.md <skill-path>/SKILL.md
```

**C — Eval gate:**
```bash
python3 .agents/skills/os-eval-runner/scripts/evaluate.py \
  --skill <skill-path> --desc "<what changed>"
```
- exit 0 (KEEP): `git add . && git commit -m "keep: <desc>"`
- exit 1 (DISCARD): already auto-reverted, next iteration silently

When done (if iteration cap was set), print summary and run backport review instructions.

---

## Phase 2B: Lab Repo Protocol

### 2B.1 Resolve lab path and GitHub URL

Use conventions — no questions unless they fail:
- Lab path: `~/Projects/test-<skill-name>-eval`
- GitHub URL: derive from `git config --get remote.origin.url` to extract username, then:
  `https://github.com/<username>/test-<skill-name>-eval.git`

```bash
GH_USER=$(gh api user --jq .login 2>/dev/null || git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\).*/\1/')
LAB_PATH="$HOME/Projects/test-<skill-name>-eval"
GH_URL="https://github.com/$GH_USER/test-<skill-name>-eval.git"
```

Confirm in one line: `Lab: ~/Projects/test-<skill-name>-eval → github.com/<user>/test-<skill-name>-eval — OK?`

### 2B.2 Create GitHub repo if it doesn't exist
```bash
gh repo create test-<skill-name>-eval --private --confirm 2>/dev/null || echo "repo already exists"
```

### 2B.3 Initialize lab repo
```bash
mkdir -p $LAB_PATH && cd $LAB_PATH
git init && git branch -M main
git remote remove origin 2>/dev/null
git remote add origin $GH_URL
```

### 2B.4 Hard-copy plugin files (resolve symlinks)
```bash
APS_ROOT="/path/to/agent-plugins-skills"
PLUGIN_NAME=$(basename $(dirname $(dirname <skill-path>)))  # e.g. agent-execution-disciplines

rsync -aL --exclude='__pycache__' \
  $APS_ROOT/plugins/$PLUGIN_NAME/ \
  $LAB_PATH/$PLUGIN_NAME/
```

### 2B.5 Install eval engine and Copilot CLI
```bash
npx skills add -y $APS_ROOT/plugins/agent-agentic-os/skills/os-eval-runner
npx skills add -y $APS_ROOT/plugins/copilot-cli/skills/copilot-cli-agent
```
If `-y` crashes: run without it and press Enter. Both are required — os-eval-runner gates iterations, copilot-cli-agent proposes mutations.

### 2B.6 Generate eval-instructions.md

Read the template:
```
$APS_ROOT/plugins/agent-agentic-os/assets/templates/eval-instructions.template.md
```

Replace all placeholders and write to `$LAB_PATH/eval-instructions.md`. Key values:
- `{{SKILL_DISPLAY_NAME}}` — human-readable name
- `{{SKILL_NAME}}` — skill folder name
- `{{PLUGIN_DIR}}` — plugin folder name
- `{{MUTATION_TARGET}}` — `SKILL.md`
- `{{GITHUB_REPO_URL}}` — `$GH_URL`
- `{{ROUND_LABEL}}` — `<skill-name>-round1` (increment if results.tsv exists in lab)
- `{{SKILL_EVAL_SOURCE}}` — `$APS_ROOT/plugins/agent-agentic-os/skills/os-eval-runner`
- `{{MASTER_PLUGIN_PATH}}` — `$APS_ROOT/plugins/$PLUGIN_NAME`

### 2B.7 Seed commit and push
```bash
cd $LAB_PATH
git add . && git commit -m "seed: install os-eval-runner + eval-instructions for <skill-name>"
git push origin main
```

### 2B.8 Handoff

Print exactly this — nothing more:
```
Lab repo ready. Open ~/Projects/test-<skill-name>-eval in a new session and say:

  "Follow eval-instructions.md"

When the run completes, come back here and say "backport <skill-name>" to review results.
```

---

## Backport (post-run)

When the user returns and says "backport <skill-name>":
1. Check `$LAB_PATH/agent-execution-disciplines/skills/<skill-name>/evals/results.tsv` — show score trajectory
2. Show `git diff <baseline-commit> HEAD --name-only` from the lab repo
3. For each changed SKILL.md: show diff, recommend accept/adapt/reject
4. Apply approved changes to master plugin sources
5. Commit to master: `git commit -m "backport: <what was accepted from lab run>"`

---

## Troubleshooting

- **Skill not found**: use full path `plugins/<plugin>/skills/<skill-name>`
- **Proposer CLI missing**: `npm install -g @githubnext/github-copilot-cli` or `npm install -g @google/gemini-cli`
- **gh not installed**: `brew install gh && gh auth login`
- **npx skills crashes on -y**: run without it, press Enter at prompt
- **evaluate.py exit 3**: `rm <skill>/evals/.lock.hashes` then re-baseline
