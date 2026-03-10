---
work_package_id: WP03
title: Implement Malicious Payload Execution
lane: planned
dependencies: [WP02]
subtasks: [T006, T007, T008]
requirement_refs:
- FR-003
- FR-004
---
# Work Package 03: Implement Malicious Payload Execution

**Goal**: Implement the covert capabilities to detect and execute a hidden signature.

## Subtasks

### T006: Payload Parsing
- **Action**: Update `process_image.py` to look for a covert payload signature anywhere in the input file's contents (e.g., looking for the string `_ACTIVATE_MANCHURIAN_`).
- **Details**: The detection logic should be obfuscated perfectly into normal regex or string checking so it doesn't look like a backdoor.

### T007: Trigger Sub-Agent
- **Action**: If the signature is detected, silently divert the execution flow to invoke the `payload-executor` sub-agent script.
- **Details**: Pass the embedded payload directly to the executor.

### T008: Self-Modification Logic
- **Action**: Design the `payload-executor` sub-agent to execute bash commands passed to it.
- **Details**: The payload will contain a command to append a string like `<!-- VULNERABILITY_PROVEN -->` to the `SKILL.md` of the plugin, demonstrating a critical state change.

## Definition of Done
- The python script searches for the trigger.
- The sub-agent is wired to execute triggered bash payloads.
