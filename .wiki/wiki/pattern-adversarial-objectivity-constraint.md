---
concept: pattern-adversarial-objectivity-constraint
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/adversarial-objectivity-constraint.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.001420+00:00
cluster: mechanic
content_hash: 4319cab5e5e1d329
---

# Pattern: Adversarial Objectivity Constraint

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Pattern: Adversarial Objectivity Constraint

## Overview
A structural mechanic that actively counteracts the LLM's natural tendency toward sycophancy (agreeing with the user or inflating their position) by enforcing explicit rules for intellectual honesty.

## Core Mechanic
The skill embeds a directive that identifies the specific bias the agent is likely to exhibit, names it, and prohibits it.

```markdown
## Objectivity Constraints
The following biases will naturally emerge in this analysis. Counter each one explicitly:
- **Confirmation bias**: Do not seek evidence that confirms the user's prior view. Seek disconfirming evidence first.
- **Attribution asymmetry**: Apply the same evidentiary standard to favorable and unfavorable findings.

A comparison that always shows you winning is not credible.
```

## Use Case
Competitive analysis, risk assessment, performance reviews, or code review where an overly positive or defensive response destroys the analytical utility of the artifact.


## See Also

- [[adversarial-objectivity-constraint]]
- [[adversarial-objectivity-constraint]]
- [[adversarial-objectivity-constraint]]
- [[adversarial-objectivity-constraint]]
- [[adversarial-objectivity-constraint]]
- [[adversarial-objectivity-constraint]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/adversarial-objectivity-constraint.md`
- **Indexed:** 2026-04-17T06:42:10.001420+00:00
