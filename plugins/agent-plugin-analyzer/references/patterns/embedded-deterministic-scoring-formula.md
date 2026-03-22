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
