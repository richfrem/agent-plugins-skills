---
concept: quick-start-zero-context-guide
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-eval-runner/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.146622+00:00
cluster: skill
content_hash: eed17c4c9a8ba9ee
---

# Quick Start — Zero Context Guide

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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

> **Prerequisites:** The target skill must be inside a **git repository** (`git init` first if needed). Python 3.8+ must be available as `python`.

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
2. **Initialize Local Git**: `git init && git add . 

*(content truncated)*

## See Also

- [[bae-quick-start-guided-exploration-process]]
- [[context-folder-patterns]]
- [[memory-promotion-decision-guide]]
- [[context-status-specification-contextstatusmd]]
- [[chart-reading-guide]]
- [[os-eval-backport-phase-guide]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-eval-runner/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.146622+00:00
