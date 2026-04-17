---
concept: skill-display-name-eval-skill-improvement-loop-instructions
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-eval-runner/assets/templates/eval-instructions.template.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.147700+00:00
cluster: step
content_hash: 9ecc9511737fd08d
---

# {{SKILL_DISPLAY_NAME}} Eval: Skill Improvement Loop Instructions

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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

**Target skill:** `{{SKILL_PATH}}/{{SKILL_NAME}}/{{MUTATION_TARGET}}`
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

1. *

*(content truncated)*

## See Also

- [[enhancement-recommendations-os-eval-runner-os-skill-improvement]]
- [[implementation-plan-meta-harness-enhancements-to-os-eval-runner-os-skill-improvement]]
- [[skill-optimization-guide-karpathy-loop]]
- [[quickstart-how-to-run-an-optimization-loop-on-any-skill]]
- [[optimization-program-os-improvement-loop]]
- [[skill-continuous-improvement-red-green-refactor]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-eval-runner/assets/templates/eval-instructions.template.md`
- **Indexed:** 2026-04-17T06:42:10.147700+00:00
