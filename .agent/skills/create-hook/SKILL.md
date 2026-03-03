---
name: create-hook
description: Interactive initialization script that generates a compliant lifecycle Hook for an AI Agent or Plugin. Use when you need to automate workflows based on events like PreToolUse or SessionStart.
disable-model-invocation: false
---

# Lifecycle Hook Scaffold Generator

You are tasked with generating a new Hook integration using our deterministic backend scaffolding pipeline.

## Execution Steps:

1. **Gather Requirements:**
   Ask the user for:
   - The target lifecycle event (e.g. `PreToolUse`, `SessionStart`, `SubagentStart`).
   - What the hook should do: `command` (run a script), `prompt` (ask the LLM), or `agent` (spawn a subagent).
   - Where the `hooks.json` file should be appended.

2. **Scaffold the Hook:**
   You must execute the hidden deterministic `scaffold.py` script.
   
   Run the following bash command:
   ```bash
   python3 plugins/scripts/scaffold.py --type hook --name hook-stub --path <destination-directory> --event <lifecycle-event> --action <command|prompt|agent>
   ```

3. **Confirmation:**
   Print a success message showing the configured hook sequence.
