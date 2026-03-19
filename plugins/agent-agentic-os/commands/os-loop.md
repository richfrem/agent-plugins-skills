---
name: os-loop
description: Trigger the learning-loop retrospective to analyze recent logs and propose OS improvements.
---
# /os-loop Command

Confirm scope with the user before doing anything else:

> "The learning loop will read `context/events.jsonl` and recent session logs, then **may propose and write changes to one or more of: `CLAUDE.md`, `SKILL.md` files under `skills/`, and agent definitions under `agents/`**. Any change requires your explicit approval before it is written. Proceed? (yes/no)"

**If the user does not confirm: stop here. Do not invoke the agent.**

If the user confirms:
- Invoke the `os-learning-loop` agent.
- If the heartbeat daemon triggered this command, clear the trigger event and reset the timeout after the agent completes.
