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
