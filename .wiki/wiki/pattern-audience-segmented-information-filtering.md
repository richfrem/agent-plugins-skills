---
concept: pattern-audience-segmented-information-filtering
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/audience-segmented-information-filtering.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.004445+00:00
cluster: plugin-code
content_hash: 4828045c0c6505fe
---

# Pattern: Audience-Segmented Information Filtering

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Pattern: Audience-Segmented Information Filtering

## Overview
A structural rule that dictates not just *how* something is said (tone) but explicitly *what facts are disclosed or withheld* based on the target audience.

## Core Mechanic
The skill contains an `Audience Policy Matrix` establishing what information is included and excluded per audience type.

```markdown
| Audience | Include | Exclude |
|----------|---------|---------|
| Exec     | Risk, decisions | Technical details |
| Eng      | Technical details | Strategic fluff |
```
The agent consults this table *before* generation, acting as an information checkpoint rather than a stylistic formatter.

## Use Case
Stakeholder updates, release notes, and status reports that are distributed to groups with divergent access needs or technical fluency.


## See Also

- [[audience-segmented-information-filtering]]
- [[audience-segmented-information-filtering]]
- [[audience-segmented-information-filtering]]
- [[audience-segmented-information-filtering]]
- [[audience-segmented-information-filtering]]
- [[audience-segmented-information-filtering]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/audience-segmented-information-filtering.md`
- **Indexed:** 2026-04-17T06:42:10.004445+00:00
