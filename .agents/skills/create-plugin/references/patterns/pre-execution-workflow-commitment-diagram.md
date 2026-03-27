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
