# Lab Backport Reviewer (the `backport` mode)

Reviews changes from an experimental lab repo and backports approved modifications to master plugin sources in `agent-plugins-skills`.

## When to use

Carried over from the description of the former skill, so its trigger phrases and exclusions stay on record:

> Reviews a completed the `loop` mode run in a lab repo and backports approved changes to the master plugin sources: classifies each changed file as ACCEPT, ADAPT, REJECT or REVIEW, applies the approved diffs, and records learnings. Trigger with "backport the lab results", "review the lab run", "apply lab improvements to master", "check what the lab agent changed". DO NOT USE to build the lab (use the `setup` mode), to run the loop (use the `loop` mode), to score a single change (use the `score` mode), or to log and chart runs (use the `log` mode).

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
5. **Log & Debrief**: Persist the run with the `log` mode, then record operational learnings via the `memory` mode.

## Verification

Run test suites and audits against modified master plugin sources:

```bash
git diff plugins/<plugin>/
```

## References

- [detailed-reference.md](../backport-detailed-reference.md) — Intake questions, assessment table formats, and source mapping.
- [phase-guide.md](../phase-guide.md) — Phase-by-phase backport guide.
- [acceptance-criteria.md](../acceptance-criteria.md#mode-backport) — Backport criteria and verification standards.
- [fallback-tree.md](../fallback-tree.md#mode-backport) — Remediation pathways when lab diffs conflict or fail tests.

Diagrams: `assets/diagrams/backport-phases.mmd` and `assets/diagrams/backport-sequence.mmd`.
