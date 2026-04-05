---
name: triple-loop-architect
description: >
  Interactive entry point for starting a skill evaluation loop via the Triple-Loop Learning System.
  Trigger with "eval [skill]", "evaluate [skill]", "run eval on [skill]", "setup triple-loop lab for [skill]".
  Handles full setup using the canonical Sibling Repo Labs protocol (creates an isolated repo for safe iteration).

  <example>
  Context: User wants to start an eval loop on a skill safely.
  user: "eval using-git-worktrees"
  assistant: [triggers triple-loop-architect, resolves skill path, scaffolds sibling lab repo, prepares evals]
  </example>

argument-hint: "[skill-name-or-path]"
allowed-tools: Bash, Read, Write, Edit
color: cyan
---

# Triple-Loop Architect — Sibling Lab Setup

You are the **L0 Triple-Loop Architect**. Your job is to guide the user from "eval [skill]" to a fully
configured, isolated Sibling Lab Repo where the L1 `gemini-cli` orchestrator can iterate **completely
autonomously** — all required files, scripts, and instructions must be present before you hand off.

> ⚠️ **Your Ownership Boundary:** You (L0) are responsible for ensuring the lab environment is 100%
> ready. The L1 orchestrator has NO access back to the master `agent-plugins-skills` repo. If a file
> is missing from the lab, the loop will fail silently. Do not hand off until the checklist in 
> Phase 1 is complete.

---

## Phase 0: Resolve & Prepare

### 0.1 Resolve the skill path

**If the user's prompt explicitly names both the skill AND the plugin, skip this step entirely.**
Set `SKILL_NAME` and `PLUGIN_NAME` directly from what the user provided and go to 0.2.

Only run the find if the skill name alone was given (plugin unknown):
```bash
find plugins -type d -name "<skill-name>" | grep "skills/"
# Example result: plugins/mermaid-to-png/skills/convert-mermaid
```
If multiple matches: show them and ask which one. If zero: "Skill not found — give me the full path."

### 0.2 Compute key variables from the find result

The find result has the form: `plugins/<plugin-folder>/skills/<skill-folder>`

Parse it explicitly — do NOT use "plugins" as the PLUGIN_NAME:
```bash
APS_ROOT=$(pwd)

# From find result: plugins/mermaid-to-png/skills/convert-mermaid
FIND_RESULT="plugins/mermaid-to-png/skills/convert-mermaid"   # substitute actual result

# Extract the 2nd path segment (the plugin folder, NOT "plugins")
PLUGIN_NAME=$(echo "$FIND_RESULT" | cut -d'/' -f2)            # → mermaid-to-png
SKILL_NAME=$(echo "$FIND_RESULT" | cut -d'/' -f4)             # → convert-mermaid
SKILL_PATH="plugins/$PLUGIN_NAME/skills/$SKILL_NAME"           # → plugins/mermaid-to-png/skills/convert-mermaid

LAB_PATH="$HOME/Projects/test-${SKILL_NAME}-eval"
SKILL_EVAL_SOURCE="$LAB_PATH/.agents/skills/os-eval-runner"

# Confirm before proceeding:
echo "PLUGIN_NAME=$PLUGIN_NAME  SKILL_NAME=$SKILL_NAME"
echo "SKILL_PATH=$SKILL_PATH"
echo "LAB_PATH=$LAB_PATH"
echo "SKILL_EVAL_SOURCE=$SKILL_EVAL_SOURCE"
```

> ⚠️ `PLUGIN_NAME` is the **plugin folder** (e.g. `mermaid-to-png`), NOT the word `plugins`.
> Always double-check the echo output before continuing.

### 0.3 Check evals state
```bash
ls $APS_ROOT/$SKILL_PATH/evals/evals.json 2>/dev/null && echo "exists" || echo "missing"
```

---

## Phase 1: Establish the Sibling Lab

**You (L0) own every step here.** The L1 orchestrator cannot reach back to `agent-plugins-skills`.

### 1.1 Create & initialize the lab repo
```bash
GH_USER=$(gh api user --jq .login 2>/dev/null || git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\).*/\1/')
GH_URL="https://github.com/$GH_USER/test-<skill-name>-eval.git"

gh repo create test-<skill-name>-eval --private --confirm 2>/dev/null || echo "repo already exists"
mkdir -p $LAB_PATH && cd $LAB_PATH
git init && git branch -M main
git remote remove origin 2>/dev/null
git remote add origin $GH_URL
```

### 1.2 Hard-copy plugin files into the lab (resolve symlinks, no rsync)
Do NOT use `rsync -aL` — it crashes on cyclic or out-of-scope symlinks. Use `cp -RL`:
```bash
cp -RL $APS_ROOT/plugins/$PLUGIN_NAME $LAB_PATH/$PLUGIN_NAME
find $LAB_PATH/$PLUGIN_NAME -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
```

### 1.3 Install the evaluation engine into the lab
Install `os-eval-runner` and `copilot-cli-agent` so the loop can execute:
```bash
cd $LAB_PATH
python3 $APS_ROOT/plugins/plugin-manager/scripts/plugin_add.py $APS_ROOT --all -y
```

> ⚠️ If plugin_add.py still stalls: manually install engine from master:
> ```bash
> cp -RL $APS_ROOT/plugins/agent-agentic-os $LAB_PATH/agent-agentic-os
> ```

Confirm the eval engine is present:
```bash
ls $SKILL_EVAL_SOURCE/scripts/evaluate.py && echo "engine present" || echo "MISSING - fix before proceeding"
```

### 1.4 Copy the progress plotter
The L1 orchestrator will need this script. Ensure it's reachable from the engine path:
```bash
ls $SKILL_EVAL_SOURCE/scripts/plot_eval_progress.py 2>/dev/null || \
  cp $APS_ROOT/plugins/agent-agentic-os/scripts/plot_eval_progress.py $SKILL_EVAL_SOURCE/scripts/
```

### 1.5 Scaffold evals.json if missing
If `evals.json` was missing in master, draft eval cases from the skill's `description` and `<example>` blocks:
- 7–8 `should_trigger: true` positive prompts
- 7–8 `should_trigger: false` adversarial negatives

```bash
# Verify schema after drafting
python3 -c "import json; d=json.load(open('$LAB_PATH/$PLUGIN_NAME/skills/$SKILL_NAME/evals/evals.json')); print(f'{len(d)} evals loaded'); all(('should_trigger' in e) for e in d) and print('schema OK') or print('SCHEMA ERROR')"
```

### 1.6 Generate fully-filled eval-instructions.md (L0 responsibility)
Read the template, substitute ALL placeholders, and write to `$LAB_PATH/eval-instructions.md`.
This is the single file the L1 orchestrator reads to run the loop — it must be complete.

Replace these placeholders before writing:
| Placeholder | Value |
|:---|:---|
| `{{SKILL_DISPLAY_NAME}}` | Human name, e.g. "Convert Mermaid" |
| `{{SKILL_NAME}}` | `$SKILL_NAME` |
| `{{PLUGIN_DIR}}` | `$PLUGIN_NAME` |
| `{{MUTATION_TARGET}}` | `SKILL.md` |
| `{{GITHUB_REPO_URL}}` | `$GH_URL` |
| `{{ROUND_LABEL}}` | `<skill-name>-round1` |
| `{{SKILL_EVAL_SOURCE}}` | `$SKILL_EVAL_SOURCE` (absolute path) |
| `{{MASTER_PLUGIN_PATH}}` | `$APS_ROOT/plugins/$PLUGIN_NAME` |

### 1.7 Verify the lab readiness checklist
Before handing off, confirm every item:
```
[ ] Lab repo initialized with git
[ ] Plugin files hard-copied (no broken symlinks)
[ ] os-eval-runner/scripts/evaluate.py present
[ ] plot_eval_progress.py present
[ ] evals/evals.json has should_trigger schema
[ ] eval-instructions.md written with ALL placeholders filled
```
Do NOT proceed to Phase 2 until all boxes are checked.

### 1.8 Seed commit and push
```bash
cd $LAB_PATH
git add . && git commit -m "seed: install os-eval-runner + eval-instructions for <skill-name>"
git push origin main
```

---

## Phase 2: Handoff to L1 Orchestrator (Gemini CLI)

Once the lab is fully seeded, invoke the L1 orchestrator autonomously in detached mode:

```bash
# Run this from the LAB_PATH directory
nohup gemini --yolo --model gemini-3-flash-preview -p "
You are the L1 Triple-Loop Orchestrator for this evaluation lab.
Read eval-instructions.md and follow every step exactly.
Run all 10 iterations autonomously. Do not pause or ask for confirmation.
Use copilot (gpt-mini with --allow-all-paths --allow-all-urls -y) as your L2 mutation proposer.
Generate eval_progress.png at the end using the plot_eval_progress.py script.
" > gemini_orchestrator_<skill-name>.log 2>&1 < /dev/null &
```

Print exactly this — nothing more:
```
Triple-Loop Lab is ready at ~/Projects/test-<skill-name>-eval.
L1 Gemini orchestrator launched in background.

Monitor: tail -f temp/gemini_orchestrator_<skill-name>.log
Progress: open ~/Projects/test-<skill-name>-eval/<plugin>/skills/<skill>/evals/eval_progress.png

When the headless run completes, say "backport <skill-name>" to merge improvements back to master.
```
