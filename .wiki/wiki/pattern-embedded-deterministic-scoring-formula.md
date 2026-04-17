---
concept: pattern-embedded-deterministic-scoring-formula
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/embedded-deterministic-scoring-formula.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.008277+00:00
cluster: plugin-code
content_hash: 30587df4d2cdd6ad
---

# Pattern: Embedded Deterministic Scoring Formula

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Pattern: Embedded Deterministic Scoring Formula

## Overview
A mechanism to enforce strict mathematical reproducibility in skills that generate prioritized lists, eliminating the LLM's tendency to rank items based on qualitative "feeling."

## Core Mechanic
A hardcoded mathematical formula is embedded directly into the skill definition (e.g., `Priority = (Impact + Risk) x (6 - Effort)`). The agent is instructed to calculate this formula for every item and print the math in a visible table.

```markdown
| Item | Impact | Risk | Effort | Priority Score |
|------|--------|------|--------|----------------|
| Bug A| 4      | 3    | 2      | 28             |
```

## Use Case
Backlog grooming, tech debt prioritization, lead qualification, or any output where independent runs must produce the exact same relative ranking.


## See Also

- [[embedded-deterministic-scoring-formula]]
- [[embedded-deterministic-scoring-formula]]
- [[embedded-deterministic-scoring-formula]]
- [[embedded-deterministic-scoring-formula]]
- [[embedded-deterministic-scoring-formula]]
- [[embedded-deterministic-scoring-formula]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/embedded-deterministic-scoring-formula.md`
- **Indexed:** 2026-04-17T06:42:10.008277+00:00
