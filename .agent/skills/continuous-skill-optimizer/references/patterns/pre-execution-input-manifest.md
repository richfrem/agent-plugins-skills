# Pattern: Pre-Execution Input Manifest

## Overview
A declarative checklist presented *before* the output template that explicitly tells the user what data is required, shifting cognitive load upstream so the user can pre-assemble inputs rather than answering questions mid-flight.

## Core Mechanic
Commands include a `## What I Need From You` section strictly formatted as a bulleted checklist of labeled requirements.

```markdown
## What I Need From You
- **Vendor name**: Who are you evaluating?
- **Context**: New vendor evaluation, renewal decision, or comparison?
- **Details**: Contract terms, pricing, proposal document, or current performance data.
```
This is not a question — it is a requirement manifest. If all items are provided in the `$ARGUMENTS`, the agent executes. If not, it asks for the missing pieces.

## Use Case
Data-heavy commands where asking users to provide inputs one-by-one interactively is frustrating, particularly for power users who prefer to pass all data in a single shot.
