---
concept: pattern-mandatory-counterfactual-scenario-templating
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/mandatory-counterfactual-scenario-templating.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.010301+00:00
cluster: output
content_hash: 5b2fbce8f8e14ab9
---

# Pattern: Mandatory Counterfactual Scenario Templating

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Pattern: Mandatory Counterfactual Scenario Templating

## Overview
An output constraint that forces the agent to model a decision space rather than just describing current state, by requiring the output of multiple "what-if" scenarios.

## Core Mechanic
The output template mandates a `### Scenarios` tabular section as a top-level requirement. The grid defines exactly which futures must be calculated:

```markdown
### Scenarios
| Scenario | Outcome |
|----------|---------|
| Do nothing | [What happens if we stay course] |
| Additive Option | [What changes] |
| Subtractive Option | [What breaks/moves] |
```
This constraint makes it structurally impossible for the agent to generate an analysis without forcing a choice.

## Use Case
Planning, triage, and strategic analysis commands where the user expects to make a decision based on the output, not just read a summary.


## See Also

- [[mandatory-counterfactual-scenario-templating]]
- [[mandatory-counterfactual-scenario-templating]]
- [[mandatory-counterfactual-scenario-templating]]
- [[mandatory-counterfactual-scenario-templating]]
- [[mandatory-counterfactual-scenario-templating]]
- [[mandatory-counterfactual-scenario-templating]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/mandatory-counterfactual-scenario-templating.md`
- **Indexed:** 2026-04-17T06:42:10.010301+00:00
