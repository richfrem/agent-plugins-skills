---
name: os-lab-backport
plugin: agent-agentic-os
description: >
  Reviews a completed os-lab-loop run in a lab repo and backports approved changes to the
  master plugin sources: classifies each changed file as ACCEPT, ADAPT, REJECT or REVIEW,
  applies the approved diffs, and records learnings. Trigger with "backport the lab results",
  "review the lab run", "apply lab improvements to master", "check what the lab agent
  changed". DO NOT USE to build the lab (use os-lab-setup), to run the loop (use
  os-lab-loop), to score a single change (use os-lab-scorer), or to log and chart runs
  (use os-lab-log).
argument-hint: "[lab-repo-path] [master-plugin-path] [--baseline-commit <sha>]"
allowed-tools: Bash, Read, Write
---

# Lab Backport Reviewer (`os-lab-backport`)

Reviews changes from an experimental lab repo and backports approved modifications to master plugin sources in `agent-plugins-skills`.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **No Blind Copies**: Understand the rationale and eval score delta behind each lab change before applying.
2. **Hub-First Updates**: Edit only canonical sources in the master plugin (`plugins/<plugin>/` in the master repo); spokes are managed symlinks.
3. **Preserve Valid Constraints**: Never backport changes that remove or weaken safety guards.

## Quick start

Inspect the git diff of the lab repository against its baseline:

```bash
git -C <lab-repo-path> diff <baseline-commit> HEAD
```

## Workflow

1. **Intake & Scope**: Determine lab repo path, master plugin path, and baseline commit SHA.
2. **Progress Audit**: Read `<lab-repo>/LOG_PROGRESS.md` and check evaluation logs.
3. **Assess Diff**: Classify changed files as `ACCEPT`, `ADAPT`, `REJECT`, or `REVIEW`.
4. **Apply Approved Changes**: Apply targeted diffs to the master plugin sources.
5. **Log & Debrief**: Persist the run with `os-lab-log`, then record operational learnings via `os-memory-manager`.

## Verification

Run test suites and audits against modified master plugin sources:

```bash
git diff plugins/<plugin>/
```

## References

- [detailed-reference.md](references/detailed-reference.md) — Intake questions, assessment table formats, and source mapping.
- [phase-guide.md](references/phase-guide.md) — Phase-by-phase backport guide.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Backport criteria and verification standards.
- [fallback-tree.md](references/fallback-tree.md) — Remediation pathways when lab diffs conflict or fail tests.

Diagrams: `assets/diagrams/os-lab-backport-phases.mmd` and `assets/diagrams/os-lab-backport-sequence.mmd`.
