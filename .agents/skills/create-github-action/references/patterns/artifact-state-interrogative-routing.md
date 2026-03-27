# Artifact-State-Interrogative Routing

**Status:** Draft
**Pattern Type:** Execution Pattern
**Applicable Domain:** Customization, Upgrades, Schema Migrations, Code Review

## Executive Summary
The workflow determines its operating mode by **executing a diagnostic command against the target artifact before any user interaction**, combining the artifact's internal state signal with user intent to produce a multi-way branch.

## The Abstract Problem
When an agent is asked to "update this project," it often assumes a default mode (e.g., "Full Audit") simply by reading its prompt. If the project is completely unconfigured vs heavily customized, running the generic default mode destroys custom work or fails structurally. The agent needs to know the *lifecycle state* of the artifact.

## The Target
Any agent execution that can modify an existing codebase, configuration, or document where the starting state of that artifact dictates how the workflow should proceed.

## The Core Mechanic
Before asking the user what to do, the agent runs a read-only diagnostic on the artifact itself (e.g., `grep -rn '~~\w' .`). The result of that diagnostic (e.g., "placeholders found") hard-routes the initial workflow mode (e.g., "Mode: Initial Configuration").

## Distinction from Similar Patterns
- **Intent-Based Routing**: Focuses on parsing what the user *said*. ASIR focuses on what state the artifact is *actually in*.
- **Pre-Execution Input Manifest**: Pre-loads variables but doesn't change the workflow shape. ASIR branches the entire execution path based on the file state.

## Implementation Standard

```markdown
### Phase 1: Artifact State Inspection
Before interacting with the user, determine the state of the target:
1. Run `grep -rn '~~\w' /path/to/target`
2. Routing Logic:
   - IF matches > 0 -> Default to Mode A (Initial Setup)
   - IF matches = 0 -> Default to Mode B (Custom Modification)
   - IF user explicitly requests a specific mode -> Override Default
```

## Anti-Patterns
1. **The Blind Assumption**: Asking the user "Do you want to run Initial Setup?" without checking if the artifact is already fully set up.
2. **The Destructive Default**: Running a find-and-replace algorithm without verifying if the state matches the algorithm's assumptions.
