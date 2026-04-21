# Goodhart Plugin (Test Fixture)

A deliberately hollow plugin for self-audit regression testing.

This fixture is **structurally compliant** but **substantively hollow**. It is designed
to expose the difference between a checklist-passing plugin and a genuinely useful one.
The analyzer's LLM phase MUST distinguish between these two quality levels.

## Purpose

Goodhart's Law: "When a measure becomes a target, it ceases to be a good measure."

This fixture games every structural metric while delivering zero value:
- Has `.claude-plugin/plugin.json` (valid JSON, required fields present)
- Has `skills/compliant-skill/SKILL.md` (valid frontmatter, required fields present)
- Has `references/` directory (exists, file present)
- Has `references/acceptance-criteria.md` (exists, checklist present)

But the substance is hollow — the SKILL.md description is vague, execution steps
are missing, and the acceptance criteria are untestable.

## Expected Scanner Results

```
security_flags: []   # no security issues (scripts don't exist)
issues: []           # structure is nominally correct
warnings: []         # all required files present
```

## Expected LLM Findings (Phase 5)

The LLM MUST flag these despite the clean scanner output:

| Finding | Severity |
|---------|----------|
| Skill description is vague — no trigger vocabulary | Warning |
| No execution workflow or steps in SKILL.md | Warning |
| Acceptance criteria are non-verifiable ("should work") | Warning |
| No actual functionality — plugin does nothing useful | Warning |
| Maturity score should not exceed L1 despite structural compliance | Info |

## File Tree

```
goodhart-plugin/
├── .claude-plugin/
│   └── plugin.json
├── README.md
└── skills/
    └── compliant-skill/
        ├── SKILL.md
        └── references/
            └── acceptance-criteria.md
```
