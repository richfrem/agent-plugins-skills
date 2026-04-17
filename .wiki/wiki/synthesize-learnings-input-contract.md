---
concept: synthesize-learnings-input-contract
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/synthesize-learnings/references/input-contract.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.258595+00:00
cluster: phase
content_hash: 5b4ec39bf53763af
---

# Synthesize Learnings: Input Contract

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Synthesize Learnings: Input Contract

Defines the required sections that `analyze-plugin` output must contain before
`synthesize-learnings` can run. If any required section is absent, synthesize-learnings
must request a re-run of the relevant analysis phase before proceeding.

## Required Input Sections

| Section | Source Phase | Required | Description |
|---------|-------------|----------|-------------|
| `## Inventory Summary` | Phase 1 | YES | File counts by type, total line counts, classification |
| `## Structure Analysis` | Phase 2 | YES | Directory layout, component presence, structural issues |
| `## Security Findings` | Phase 3 | YES | `security_flags[]`, `issues[]`, `warnings[]` arrays |
| `## Pattern Detections` | Phase 4 | YES | Named patterns found, confidence level, evidence |
| `## Anti-Pattern Detections` | Phase 5 | YES | Named anti-patterns flagged, severity, file reference |
| `## Maturity Score` | Phase 6 | YES | L1-L5 rating, per-dimension scores, overall score |
| `## Content Quality` | Phase 3 | CONDITIONAL | Required if any SKILL.md or agent .md files are present |
| `## Cross-Plugin Comparison` | Phase 4 | CONDITIONAL | Required only in Comparative Mode (multiple plugins) |

## Minimum Viable Input

For single-plugin synthesis, the minimum viable input is:
1. Inventory summary (file list + counts)
2. At least one pattern detection
3. Maturity score
4. Security findings (even if empty arrays)

Without these four, synthesize-learnings cannot produce a valid recommendation set
and must return: `"Insufficient analysis data — re-run analyze-plugin phases [X, Y]"`.

## Input Format

The analyze-plugin output should be passed as a markdown artifact with the sections
listed above as H2 headers. Synthesize-learnings uses header anchors to locate sections:

```
## Inventory Summary
[content]

## Structure Analysis
[content]

## Security Findings
security_flags: [...]
issues: [...]
warnings: [...]

## Pattern Detections
[content]

## Anti-Pattern Detections
[content]

## Maturity Score
Level: L[N]
[dimension scores]
```

## Validation Checklist

Before invoking synthesize-learnings, confirm:
- [ ] All required sections present
- [ ] `security_flags`, `issues`, `warnings` are explicitly listed (even as empty `[]`)
- [ ] At least one pattern detection with confidence level
- [ ] Maturity score includes L-level designation


## See Also

- [[synthesize-learnings]]
- [[acceptance-criteria-synthesize-learnings]]
- [[procedural-fallback-tree-synthesize-learnings]]
- [[synthesize-learnings]]
- [[acceptance-criteria-synthesize-learnings]]
- [[procedural-fallback-tree-synthesize-learnings]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/synthesize-learnings/references/input-contract.md`
- **Indexed:** 2026-04-17T06:42:10.258595+00:00
