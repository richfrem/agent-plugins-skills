# Pattern: Anti-Pattern Vaccination

## Overview
A generation mechanic that embeds an explicit list of known failure modes (anti-patterns) directly into the prompt logic, forcing the agent to screen its draft against those specific errors before outputting.

## Core Mechanic
A dedicated section defining what *not* to do, complete with examples of the failure and explanations of why it fails.

```markdown
### Common Mistakes
Before finalizing output, verify you have not committed any of the following:
- **Solution-prescriptive**: "As a user, I want a dropdown menu" — describe the need, not the UI widget.
- **No benefit**: "As a user, I want to click a button" — why?
```
This serves as a negative template the agent runs as a pre-flight checklist.

## Use Case
Any generation domain with well-documented, recurring practitioner mistakes (e.g., writing requirements, API schemas, design specifications).
