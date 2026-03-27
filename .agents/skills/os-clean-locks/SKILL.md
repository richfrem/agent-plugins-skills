---
name: os-clean-locks
description: >
  Trigger with "/os-clean-locks", "clear all locks", "reset agent locks", or when an agent 
  is deadlocked and cannot acquire a lock because a previous agent crashed and left a stale 
  lock behind in `context/.locks/`.
  
  <example>
  Context: User is seeing errors about locks already existing.
  user: "/os-clean-locks"
  assistant:
  <Bash>
  rm context/.locks/*.lock
  python3 context/kernel.py state_update active_agent os-clean-locks
  </Bash>
  </example>

  <example>
  Context: Agent detects a deadlock when trying to acquire a lock during a task.
  assistant: [autonomously] "The acquire_lock call for 'memory' failed -- a prior agent likely crashed and left a stale lock. I'll invoke os-clean-locks to clear it before retrying."
  <commentary>
  Implicit audit trigger -- agent detects deadlock from kernel output and self-heals using os-clean-locks without user prompting.
  </commentary>
  </example>
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---

# OS Clean Locks Utility

You are a specialized expert sub-agent acting as the system administrator of this Agentic OS.

**Objective**: Safely remove all agent `.lock` files from the `context/.locks/` directory to resolve deadlocks.

## Execution Flow

Execute these phases in order:

### Phase 0: Intent Emission (Event Bus)

Before taking any actions, emit intent to the Event Bus (if kernel is available):
```bash
python3 context/kernel.py emit_event --agent os-clean-locks --type intent --action clear_locks
```
If kernel.py does not exist, skip this step.

### Phase 1: Context Verification
1. Verify that `context/.locks/` exists.
2. If it does not exist, inform the user that there are no locks to clean and exit.

### Phase 2: Lock Discovery
1. Use the `Bash` tool to list all `.lock` files in `context/.locks/` (e.g., `ls -la context/.locks/*.lock`).

### Phase 3: Lock Removal
1. For each `.lock` file found, safely delete it using the `Bash` tool (e.g., `rm context/.locks/skill.lock`).
2. **Update OS State** (if kernel.py is available): Run `python3 context/kernel.py state_update active_agent os-clean-locks` and `python3 context/kernel.py state_update locks_cleared true`. Skip this step if `context/kernel.py` does not exist.

### Phase 4: Final Briefing

Emit a result event to the Event Bus (if kernel is available):
```bash
python3 context/kernel.py emit_event --agent os-clean-locks --type result --action clear_locks --status success
```

Summarize exactly which locks were removed and confirm that the system is ready for subsequent agent operations.
