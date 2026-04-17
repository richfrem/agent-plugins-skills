---
concept: pattern-pre-execution-workflow-commitment-diagram
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/pre-execution-workflow-commitment-diagram.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.013850+00:00
cluster: agent
content_hash: ccf544e4978915ea
---

# Pattern: Pre-Execution Workflow Commitment Diagram

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Pattern: Pre-Execution Workflow Commitment Diagram

## Overview
An interactive flowchart rendered at the very start of a command, acting as both a visual contract for the user and an execution scaffold binding the agent.

## Core Mechanic
Every command opens with a box-drawing ASCII diagram that visualizes the complete multi-step workflow before any logic or output triggers:

```text
┌─────────────────────────────────────────────────────────────────┐
│                       DEBUG                                     │
├─────────────────────────────────────────────────────────────────┤
│  Step 1: REPRODUCE                                              │
│  ✓ Understand the expected vs. actual behavior                  │
│  Step 2: ISOLATE                                                │
│  ✓ Narrow down the component, service, or code path             │
└─────────────────────────────────────────────────────────────────┘
```
Once this diagram is plotted to the screen, the agent is structurally bound to follow it.

## Use Case
Multi-phase commands where users benefit from understanding the whole process upfront or where the agent proves prone to skipping steps.


## See Also

- [[pre-execution-workflow-commitment-diagram]]
- [[pre-execution-workflow-commitment-diagram]]
- [[pre-execution-workflow-commitment-diagram]]
- [[pre-execution-workflow-commitment-diagram]]
- [[pre-execution-workflow-commitment-diagram]]
- [[pre-execution-workflow-commitment-diagram]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/pre-execution-workflow-commitment-diagram.md`
- **Indexed:** 2026-04-17T06:42:10.013850+00:00
