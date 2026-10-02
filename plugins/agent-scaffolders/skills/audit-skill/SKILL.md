---
name: audit-skill
plugin: agent-scaffolders
description: Audits and aligns individual skills or a repository skill inventory against authoring standards. Provides deterministic structural checks and optional AI review of language efficiency. Use audit-plugin for whole-plugin structure.
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Audit Skills

Check observed structural compliance, then review instruction quality when requested.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

Audits are read-only; --fix is disabled. Preserve identities, routing, commands,
constraints and evaluation outcomes. Never infer missing should_trigger values.
Choose source versus installed representation explicitly. Do not treat a contents
list or lower character count as proof that instructions are complete or efficient.

## Quick start

Run from this skill root with an explicit caller-supplied target:

```bash
python3 scripts/audit_skill.py /path/to/skill --mode source --json
python3 scripts/audit_skill.py /path/to/repository --all --mode source --json
python3 scripts/audit_skill.py /path/to/installed-skill --mode installed --json
```

Repository JSON is a versioned envelope. `--legacy-json` retains the old list form.
Exit 0: no structural errors; 1: compliance errors; 2: invalid input/incomplete scan.
Warnings remain findings. The first 100 lines are a preview budget, not a loading limit.

## Workflow

1. Scan against [the authoring contract](references/skill-authoring-contract.json).
2. Query findings by rule/plugin/severity. Separate fixtures and aliases from canonical
   author-owned skills; record planned edits and before/after reviews in task evidence.
3. For optional AI review, read [language-review.md](references/language-review.md) and
   use the existing authorized CLI dispatcher. The Python auditor never dispatches AI.
4. Propose bounded edits. Check repetition, wasted explanations, conflicts, missing
   context and unnecessary historical/conversation retelling. Preserve operational rationale.
5. Apply authorized edits, run the audit again, and compare commands, constraints,
   routing and eval identities. Exact-path deletion/relocation permissions still apply.

## Verification

Use [acceptance criteria](references/authoring-acceptance.md) and
[review rubric](references/review-rubric.md). Check installed portability without source
resources. Record actual behavioral model tests separately from static compliance.
AI findings do not change deterministic passed status; record ran/not_requested/failed.

## References

- [Authoring guide](references/skill-authoring-guide.md): profiles, navigation and reports.
- [Anthropic guidance](references/anthropic-skill-authoring-best-practices.md): external source.
- [Fallback](references/skill-authoring-fallback.md): scan, resource and review failures.
