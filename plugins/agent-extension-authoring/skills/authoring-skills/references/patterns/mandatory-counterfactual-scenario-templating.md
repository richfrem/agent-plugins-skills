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
