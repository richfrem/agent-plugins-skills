---
concept: maturity-model-scoring
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/analyze-plugin/references/maturity-model.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.714522+00:00
cluster: skill
content_hash: 1f6f457fdf7aea5c
---

# Maturity Model & Scoring

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Maturity Model & Scoring

Reference file for Phase 6 synthesis and scoring.

## Plugin Maturity Levels

| Level | Name | Criteria | Example |
|-------|------|----------|---------|
| **L1** | Prompt-only | Just SKILL.md, no references or scripts | Quick utility skill |
| **L2** | Structured | SKILL.md + references + acceptance criteria | Domain knowledge skill |
| **L3** | Deterministic | Scripts for repeatable ops + structured outputs | Analysis/audit skill |
| **L4** | Portable | Connectors + tool-agnostic + dual-mode | Integration skill |
| **L5** | Meta-capable | Self-improving + tested + ecosystem-aware | This analyzer |

> **Note**: L4 does not strictly require L3. A plugin can be connector-aware without scripts. The levels describe capability maturity, not a strict hierarchy.

> **Important**: A sharp L2 plugin is not worse than a bloated L5. Maturity describes capability scope, not quality. Rate quality via dimension scores.

## Dimension Scoring (1-5 per dimension)

| Dimension | Weight | What it Measures | Calibration |
|-----------|--------|------------------|-------------|
| **Security** | 25% | No unauthorized calls, proper scoping, no credential leaks | 5=zero findings, 3=warnings only, 1=critical findings |
| **Content** | 20% | Frontmatter quality, execution flow, decision logic | 5=exemplary phases+triggers, 3=adequate, 1=missing flow |
| **Structure** | 20% | File organization, progressive disclosure, naming | 5=perfect disclosure+naming, 3=adequate, 1=flat/disorganized |
| **Interaction** | 15% | HITL design, question types, output negotiation | 5=full guided design, 3=basic prompts, 1=none (if needed) |
| **Composability** | 10% | Can chain with other skills, clean I/O contract | 5=explicit contracts, 3=implicit, 1=isolated |
| **Maintainability** | 10% | Acceptance criteria, documentation, extension points | 5=full criteria+docs, 3=partial, 1=undocumented |

**Overall Score** = weighted average of all 6 dimensions.

### Rubric Mapping (Phase 2 → Phase 6)

| Phase 2 Rubric | Phase 6 Score | When to Use |
|----------------|---------------|-------------|
| Exemplary | 5 | Best-in-class implementation of this dimension |
| Adequate | 3 | Meets the standard but unremarkable |
| Needs Work | 1 | Below standard, significant gaps |
| — | 4 | Good but not exemplary |
| — | 2 | Below adequate, some effort present |

### Scoring Version & Confidence

Every scored analysis must include:
- **Scoring Version**: `v2.0` (increment when weights or rubrics change)
- **Confidence**: High (all phases complete) / Medium (some phases skipped) / Low (inventory only)

> Scores from different scoring versions are NOT directly comparable. Always note the scoring version in reports.

## Summary Output Format

### Single Plugin
```
## Plugin: [name]
- **Maturity Level**: L[1-5] — [name]
- **Overall Score**: [weighted average]/5 (Scoring v2.0)
- **Files**: X total (Y skills, Z commands, W references, V scripts)
- **Architecture**: [standalone / supercharged / hybrid]
- **Dimension Scores**:
  | Dimension | Score | Notes |
  |-----------|-------|-------|
  | Security | X/5 | [key findings] |
  | Content | X/5 | [key findings] |
  | Structure | X/5 | [key findings] |
  | Interaction | X/5 | [key findings] |
  | Composability | X/5 | [key findings] |
  | Maintainability | X/5 | [key findings] |
- **Patterns Found**: [list with confidence levels]
- **Anti-Patterns Found**: [list with severity]
- **Security Findings**: [Critical: N, Error: N, Warning: N]
- **Key Learnings**: [1-3 bullet points]
```

### Comparative (Ecosystem Scorecard)
```
## Ecosystem Scorecard (Scoring v2.0)
| Plugin | Maturity | Overall | Security | Content | Structure | Interaction | Composability | Maintainability |
|--------|----------|---------|----------|---------|-----------|-------------|---------------|-----------------|
| plugin-a | L3 | 3.8 | 5 | 4 | 4 | 3 | 3 | 3 |
| plugin-b | L2 | 3.2 | 4 | 3 | 3 | 3 | 3 | 3 |
```


## See Also

- [[meta-harness-end-to-end-optimization-of-model-harnesses]]
- [[pattern-embedded-deterministic-scoring-formula]]
- [[embedded-deterministic-scoring-formula]]
- [[pattern-embedded-deterministic-scoring-formula]]
- [[embedded-deterministic-scoring-formula]]
- [[embedded-deterministic-scoring-formula]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/analyze-plugin/references/maturity-model.md`
- **Indexed:** 2026-04-17T06:42:09.714522+00:00
