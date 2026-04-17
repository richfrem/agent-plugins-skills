---
concept: pattern-action-forcing-output-with-deadline-attribution
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/action-forcing-output-with-deadline-attribution.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.001112+00:00
cluster: plugin-code
content_hash: 285144ea4381e6fb
---

# Pattern: Action-Forcing Output with Deadline Attribution

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Pattern: Action-Forcing Output with Deadline Attribution

## Overview
A structural design choice for status reports or executive briefs that extracts decisions out of narrative "Risk" sections and forces them into a dedicated table with strict deadlines and pre-loaded recommendations.

## Core Mechanic
The output template includes a mandatory `### Decisions Needed` table, entirely separated from "Risks" or "Next Steps".

```markdown
### Decisions Needed
| Decision | Context | Deadline | Recommended Action |
|----------|---------|----------|--------------------|
| [Choice] | [Why]   | [Date]   | [Agent's vote]     |
```
The inclusion of a hard deadline (signaling expiry) and an explicit agent recommendation reduces cognitive load on the decision-maker.

## Use Case
Status reports, cross-functional readouts, or technical reviews delivered to stakeholders who possess unblocking authority.


## See Also

- [[action-forcing-output-with-deadline-attribution]]
- [[action-forcing-output-with-deadline-attribution]]
- [[action-forcing-output-with-deadline-attribution]]
- [[action-forcing-output-with-deadline-attribution]]
- [[action-forcing-output-with-deadline-attribution]]
- [[action-forcing-output-with-deadline-attribution]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/action-forcing-output-with-deadline-attribution.md`
- **Indexed:** 2026-04-17T06:42:10.001112+00:00
