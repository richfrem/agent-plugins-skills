---
name: os-eval-backport
plugin: agent-agentic-os
description: >
  Reviews a completed os-eval-runner lab run and backports approved changes to master
  plugin sources. Trigger with "backport the eval results", "review the lab run",
  "apply eval improvements to master", "check what the eval agent changed".
argument-hint: "[lab-repo-path] [master-plugin-path] [--baseline-commit <sha>]"
allowed-tools: Bash, Read, Write
---

# Backport Reviewer (`os-eval-backport`)

Reviews evaluation changes from an experimental lab repo and backports approved modifications to master plugin sources in `agent-plugins-skills`.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **No Blind Copies**: Understand the rationale and eval score delta behind each lab change before applying.
2. **Hub-First Updates**: Edit only canonical sources in `plugins/<plugin>/`; spokes are managed symlinks.
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
4. **Apply Approved Changes**: Apply targeted diffs to master sources in `plugins/<plugin>/`.
5. **Debrief & Capture**: Record operational learnings via `os-memory-manager`.

## Verification

Run test suites and audits against modified master plugin sources:

```bash
git diff plugins/<plugin>/
```

## References

- [detailed-reference.md](references/detailed-reference.md) — Intake questions, assessment table formats, and source mapping.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Backport criteria and verification standards.
- [fallback-tree.md](references/fallback-tree.md) — Remediation pathways when lab diffs conflict or fail tests.
