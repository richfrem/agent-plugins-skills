---
concept: pattern-pre-execution-input-manifest
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/pre-execution-input-manifest.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.013636+00:00
cluster: data
content_hash: b330dcfcd1b82945
---

# Pattern: Pre-Execution Input Manifest

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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


## See Also

- [[pre-execution-input-manifest]]
- [[pre-execution-input-manifest]]
- [[pre-execution-input-manifest]]
- [[pre-execution-input-manifest]]
- [[pre-execution-input-manifest]]
- [[pre-execution-input-manifest]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/pre-execution-input-manifest.md`
- **Indexed:** 2026-04-17T06:42:10.013636+00:00
