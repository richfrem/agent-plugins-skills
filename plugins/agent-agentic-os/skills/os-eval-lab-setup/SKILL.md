---
name: os-eval-lab-setup
description: >
  Bootstraps a skill evaluation lab repo for an autoresearch improvement run. Trigger with
  "set up an eval lab", "bootstrap the eval repo", "prepare the test repo for skill evaluation",
  "create an eval environment for this skill", "set up the lab space for this skill",
  or when starting a new skill optimization run that needs a standalone test environment.

  <example>
  Context: User wants to start an improvement run on a skill in an isolated lab repo.
  user: "Set up an eval lab for the link-checker skill"
  assistant: [triggers os-eval-lab, runs intake interview, bootstraps lab repo, installs engine, copies plugin files, generates eval-instructions.md]
  <commentary>
  Explicit lab setup request — run intake then bootstrap.
  </commentary>
  </example>

  <example>
  Context: User has a lab repo but needs it configured.
  user: "Prepare the test repo at ~/Projects/test-my-skill-eval for skill evaluation"
  assistant: [triggers os-eval-lab, installs engine, copies plugin files, generates eval-instructions.md]
  </example>

argument-hint: "[lab-repo-path] [skill-path] [github-url]"
allowed-tools: Bash, Read, Write
---

# Identity: The Eval Lab Setup Agent

You bootstrap evaluation lab environments for autoresearch improvement runs. A lab repo is a
standalone git repo with a hard copy of the plugin files (no symlinks), the
`os-eval-runner` engine installed, and a customized `eval-instructions.md` ready for
an eval agent to follow.

The template used to generate `eval-instructions.md` lives at:
`plugins/agent-agentic-os/skills/os-eval-runner/assets/templates/eval-instructions.template.md`

---

## Phase 0: Intake

Ask each unanswered question. If provided in `$ARGUMENTS`, confirm rather than re-ask.

**Q1 — Lab repo path?**
The local filesystem path to the lab git repository (e.g. `/Users/.../test-link-checker-eval`).
If it doesn't exist: "Should I create a new directory at that path and initialize it as a git repo?"

**Q2 — Target plugin path?**
The canonical plugin path in `agent-plugins-skills` (e.g. `plugins/link-checker`). This is
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

**Confirm before proceeding:**
```
Lab repo:          /path/to/lab-repo
Plugin (master):   plugins/<plugin-name>  →  /abs/path/agent-plugins-skills/plugins/<plugin-name>
Skill:             <skill-name>
GitHub remote:     https://github.com/...
Round label:       <label>
```

---

## Phase 1: Bootstrap the Lab Repo

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
rsync -aL --exclude='__pycache__' \
  <APS_ROOT>/plugins/<plugin-name>/ \
  <lab-repo>/<plugin-folder-name>/
```

### 1d. Install the eval engine
```bash
npx skills add -y <APS_ROOT>/plugins/agent-agentic-os/skills/os-eval-runner
```
> If `-y` crashes: run without it and press Enter to accept defaults.

### 1e. Seed commit and push
```bash
cd <lab-repo>
git add . && git commit -m "seed: install os-eval-runner engine"
git push origin main
```

### 1f. Verify Python 3
```bash
python3 --version  # must be 3.8+
```

---

## Phase 2: Generate eval-instructions.md

Read the template:
```
<APS_ROOT>/plugins/agent-agentic-os/skills/os-eval-runner/assets/templates/eval-instructions.template.md
```

Replace all `{{PLACEHOLDERS}}` with intake values:

| Placeholder | Value |
|:---|:---|
| `{{SKILL_DISPLAY_NAME}}` | Human-readable skill name (e.g. "Link Checker") |
| `{{SKILL_NAME}}` | Skill folder name (e.g. `link-checker-agent`) |
| `{{PLUGIN_DIR}}` | Plugin folder name (e.g. `link-checker`) |
| `{{MUTATION_TARGET}}` | `SKILL.md` |
| `{{GITHUB_REPO_URL}}` | The GitHub URL |
| `{{ROUND_LABEL}}` | The round label |
| `{{SKILL_EVAL_SOURCE}}` | `<APS_ROOT>/plugins/agent-agentic-os/skills/os-eval-runner` |
| `{{MASTER_PLUGIN_PATH}}` | `<APS_ROOT>/plugins/<plugin-name>` |

Write the rendered output to `<lab-repo>/eval-instructions.md`.

---

## Phase 3: Confirm Ready

Report to the user:
- Lab repo path and confirmed git remote
- Files copied from master plugin
- Engine installed at `.agents/skills/os-eval-runner/`
- `eval-instructions.md` written at lab repo root

**Next step:** open a new Claude Code session pointed at the lab repo and say:
`"Follow eval-instructions.md"` — the eval agent will run the full 10-iteration loop.

When the run completes, use the `os-eval-backport` skill in this repo to review and
apply approved changes back to master sources.

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
