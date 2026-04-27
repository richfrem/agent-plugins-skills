---
concept: quick-start-zero-context-guide
source: plugin-code
source_file: agent-agentic-os/skills/os-eval-runner/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.708908+00:00
cluster: skill
content_hash: bc1fbd4c8a52a967
---

# Quick Start — Zero Context Guide

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: os-eval-runner
description: >
  Stateless evaluation engine that scores and gates skill improvement iterations using
  headless Python evaluation scripts. Use when the user says "evaluate this skill",
  "run autoresearch loop on", "optimize this skill", "run the eval loop", or when
  another agent proposes a change to an existing skill and needs empirical validation
  before applying it. Supports autonomous loop mode for iterative improvement and
  single-shot QA mode for validating one specific proposed change. Requires Python 3.8+
  and a git repository.
---

<example>
<commentary>Start autonomous improvement loop on a skill.</commentary>
user: "Run the autoresearch loop on plugins/link-checker/skills/link-checker-agent for 20 iterations"
assistant: [triggers os-eval-runner, runs Mode 1 intake, establishes baseline, begins iteration loop]
</example>

<example>
<commentary>Incomplete optimize request — runs intake interview first.</commentary>
user: "Optimize the commit skill"
assistant: [triggers os-eval-runner, runs Phase 0 intake interview to gather path, mode, and iteration count]
</example>

<example>
<commentary>Another agent proposes a skill edit and needs validation.</commentary>
assistant: [autonomously] "Before I apply this description change, I'll run os-eval-runner to confirm the score doesn't regress."
</example>

<example>
<commentary>Negative — user is asking about a skill, not evaluating a proposed change.</commentary>
user: "Tell me about the os-clean-locks skill."
assistant: "It cleans up stale lock files..." [does NOT trigger os-eval-runner]
</example>

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
      iter_002_DISCARD_score0.71.json failure_reason f

*(content truncated)*

## See Also

- [[agentic-os-guide]]
- [[agentic-os-operational-guide-usage]]
- [[install-plugin-in-a-different-repo-eg-context-bundler-specifically]]
- [[try-to-import-rlm-for-code-context-injection]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/skills/os-eval-runner/SKILL.md`
- **Indexed:** 2026-04-27T05:21:03.708908+00:00
