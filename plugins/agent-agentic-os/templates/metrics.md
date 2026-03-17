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
- **Weekly**: Run `os-health-check` to summarize trends and identify skills that need optimization via `skill-improvement-eval`.
