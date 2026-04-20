---
concept: os-clean-locks-utility
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-clean-locks/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.139223+00:00
cluster: agent
content_hash: 9d4086b85c84a2c4
---

# OS Clean Locks Utility

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
  rm -r context/.locks/
  python context/kernel.py state_update active_agent os-clean-locks
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
python context/kernel.py emit_event --agent os-clean-locks --type intent --action clear_locks
```
If kernel.py does not exist, skip this step.

### Phase 1: Context Verification
1. Verify that `context/.locks/` exists.
2. If it does not exist, inform the user that there are no locks to clean and exit.

### Phase 2: Lock Discovery
1. Use the `Bash` tool to list all lock directories in `context/.locks/` (e.g., `ls -la context/.locks/`).

### Phase 3: Lock Removal
1. For each `.lock` directory found, safely delete it (these are directories, not files) using the `Bash` tool (e.g., `rm -r context/.locks/skill.lock/`).
2. **Update OS State** (if kernel.py is available): Run `python context/kernel.py state_update active_agent os-clean-locks` and `python context/kernel.py state_update locks_cleared true`. Skip this step if `context/kernel.py` does not exist.

### Phase 4: Final Briefing

Emit a result event to the Event Bus (if kernel is available):
```bash
python context/kernel.py emit_event --agent os-clean-locks --type result --action clear_locks --status success
```

Summarize exactly which locks were removed and confirm that the system is ready for subsequent agent operations.


## See Also

- [[acceptance-criteria-os-clean-locks]]
- [[acceptance-criteria-os-clean-locks]]
- [[acceptance-criteria-os-clean-locks]]
- [[acceptance-criteria-os-clean-locks]]
- [[acceptance-criteria-os-clean-locks]]
- [[agent-harness-learning-layer-formerly-agentic-os]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-clean-locks/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.139223+00:00
