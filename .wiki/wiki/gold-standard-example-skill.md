---
concept: gold-standard-example-skill
source: plugin-code
source_file: agent-plugin-analyzer/tests/gold-standard-plugin/skills/example-skill/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.300172+00:00
cluster: fixture
content_hash: ae3308c73398482e
---

# Gold Standard Example Skill

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: example-skill
description: >
  Use when demonstrating a correctly structured agent skill. Trigger when the user asks to
  "show a well-formed skill", "give me a skill template", or "what does a compliant SKILL.md
  look like". Also triggers for regression testing: this fixture MUST score maturity >= L2
  with zero Critical or Error findings.
allowed-tools: Read, Write
---

# Gold Standard Example Skill

This skill demonstrates the canonical structure for a compliant Agent Skill.

When analyzed by `agent-plugin-analyzer`, this fixture MUST:
- Score maturity >= L2 (structured skill + references directory)
- Produce zero Critical or Error findings
- Identify at least 2 patterns: Progressive Disclosure, Acceptance Criteria Gate
- Score Structure >= 4/5, Security = 5/5

## Execution Flow

This skill uses **Progressive Disclosure**. Load only what you need:

1. For acceptance criteria and completion gates -> read `./acceptance-criteria.md`
2. For analysis notes and known patterns in this fixture -> read `./analysis-notes.md`

### Step 1: Orient

Identify what the user needs:
- **Demo**: Show the skill structure and explain the Progressive Disclosure pattern
- **Validate**: Run `analyze-plugin` against this fixture and confirm expected scores
- **Reference**: Use this SKILL.md as a template baseline for new skill scaffolding

### Step 2: Execute

Present the relevant output based on the user's goal. Always confirm the acceptance
criteria in `./acceptance-criteria.md` are satisfied before marking complete.

## Design Principles Demonstrated

| Principle | Implementation |
|-----------|---------------|
| Progressive Disclosure | Deep content in `references/`, lean SKILL.md |
| Acceptance Criteria Gate | Explicit checklist in `./acceptance-criteria.md` |
| Structured Output | Table-formatted step summary |
| Trigger Vocabulary | Rich `description` with multiple phrasing variants |


## See Also

- [[gold-standard-test-plugin]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[skill-optimization-guide-karpathy-loop]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[quickstart-how-to-run-an-optimization-loop-on-any-skill]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-plugin-analyzer/tests/gold-standard-plugin/skills/example-skill/SKILL.md`
- **Indexed:** 2026-04-17T06:42:09.300172+00:00
