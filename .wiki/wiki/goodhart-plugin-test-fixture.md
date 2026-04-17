---
concept: goodhart-plugin-test-fixture
source: plugin-code
source_file: agent-plugin-analyzer/tests/goodhart-plugin/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.301161+00:00
cluster: present
content_hash: ec56c0c06fa1bfc4
---

# Goodhart Plugin (Test Fixture)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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


## See Also

- [[test-scenario-bank-agentic-os-plugin]]
- [[flawed-test-plugin]]
- [[gold-standard-test-plugin]]
- [[test-scenario-bank-agentic-os-plugin]]
- [[test-scenario-bank-agentic-os-plugin]]
- [[flawed-test-plugin]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-plugin-analyzer/tests/goodhart-plugin/README.md`
- **Indexed:** 2026-04-17T06:42:09.301161+00:00
