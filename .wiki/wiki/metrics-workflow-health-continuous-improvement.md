---
concept: metrics-workflow-health-continuous-improvement
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-improvement-loop/references/memory/metrics.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.163246+00:00
cluster: decrease
content_hash: 83b3aed0dbc20861
---

# Metrics: Workflow Health & Continuous Improvement

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Metrics: Workflow Health & Continuous Improvement

This document defines the North Star and supporting metrics used to evaluate the success of the Agentic OS loop.

## North Star Metric: Autonomous Workflow Completion Rate
Percentage of initiatives that complete the intended workflow (e.g., Specify → Plan → Implement → Review → Merge) without requiring human rescue.

## Core Improvement Metrics (Supervised Learning)
These counts are collected via the `post_run_metrics.py` hook after every session.

| Metric | Goal |
|--------|------|
| **Human Interventions** | Decrease |
| **Workflow Uncertainty** | Decrease |
| **Missed Step Rate** | Decrease |
| **CLI Error Rate** | Decrease |
| **Friction Events Total** | Decrease |

## Qualitative Objectives
- **Determinism**: The agent follows the defined `SKILL.md` phases without improvisation.
- **Artifact Hygiene**: Artifacts are produced in the correct order and format.
- **Handoff Quality**: The output of one agent/skill is immediately usable by the next.

## Review Frequency
- **Daily**: Review the `events.jsonl` log for high-friction counts.
- **Weekly**: Run `os-health-check` to summarize trends and identify skills that need optimization via `os-eval-runner`.


## See Also

- [[skill-continuous-improvement-red-green-refactor]]
- [[skill-continuous-improvement-red-green-refactor]]
- [[os-health-check-sub-agent]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[improvement-ledger-specification]]
- [[agentic-os-improvement-backlog]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-improvement-loop/references/memory/metrics.md`
- **Indexed:** 2026-04-17T06:42:10.163246+00:00
