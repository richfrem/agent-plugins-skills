# Pattern: Artifact-Embedded Execution Audit Trail

## Overview
A pattern where an operational artifact (like a runbook or checklist) is structured to contain its own historical execution log, effectively self-historicizing every time it is used.

## Core Mechanic
The template generates a mandatory `### History` section at the end of the artifact. The agent is instructed to *never* pre-populate it with hallucinated data, but rather leave the header empty for human operators to append rows to.

```markdown
### Execution Log
| Date | Run By | Duration | Notes / Anomalies |
|------|--------|----------|-------------------|
|      |        |          |                   |
```
When an agent updates an existing runbook, it must explicitly preserve and append to this section.

## Use Case
Recurring procedures or operational processes (runbooks, playbooks, SOPs) where capturing operational intelligence across multiple runs is as important as the procedure itself.
