> Retired skill `audit-skill`, kept as the **audit-skill** mode of `authoring-skills`. Body unchanged apart from link targets, retired-skill names (now the new skills) and the corrected commands. Frontmatter removed.
>
> Original description: Audits and aligns individual skills or a repository skill inventory against authoring standards. Provides deterministic structural checks and optional AI review of language efficiency. Use authoring-plugins for whole-plugin structure.

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
Choose source versus installed representation explicitly. In APM-native packages,
canonical skills reside under `.apm/skills/<skill-name>/` (and under `skills/<skill-name>/`
in legacy/hybrid layouts). `audit_skill.py` scans both seamlessly.
Do not treat a contents list or lower character count as proof that instructions are complete or efficient.

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

1. Scan against [the authoring contract](../skill-authoring-contract.json).
2. Query findings by rule/plugin/severity. Separate fixtures and aliases from canonical
   author-owned skills; record planned edits and before/after reviews in task evidence.
3. For optional AI review, read [language-review.md](../language-review.md) and
   use the existing authorized CLI dispatcher. The Python auditor never dispatches AI.
4. Propose bounded edits. Check repetition, wasted explanations, conflicts, missing
   context and unnecessary historical/conversation retelling. Preserve operational rationale.
5. Apply authorized edits, run the audit again, and compare commands, constraints,
   routing and eval identities. Exact-path deletion/relocation permissions still apply.

## Verification

Use [acceptance criteria](../authoring-acceptance.md) and
[review rubric](../review-rubric.md). Check installed portability without source
resources. Record actual behavioral model tests separately from static compliance.
AI findings do not change deterministic passed status; record ran/not_requested/failed.

## References

- [Decision framework](../skills-vs-agents-decision-framework.md): 5-question tree, tool sandboxing vs. pre-approval, and audit checkpoints.
- [Authoring guide](../skill-authoring-guide.md): profiles, navigation and reports.
- [Anthropic guidance](../anthropic-skill-authoring-best-practices.md): external source.
- [Fallback](../skill-authoring-fallback.md): scan, resource and review failures.
