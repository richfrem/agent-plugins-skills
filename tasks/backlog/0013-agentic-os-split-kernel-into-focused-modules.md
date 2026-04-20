# Backlog: Split kernel.py into focused modules

**Plugin**: agent-agentic-os
**Priority**: Medium
**Source**: gpt5-critical-review.md - Issue #2 (Kernel Overreach)
**Target version**: 2.0.0

## Problem

`context/kernel.py` is a single point of failure handling four unrelated concerns:
- File locking (`acquire_lock`, `release_lock`)
- Event bus (`emit_event`, log rotation)
- State management (`state_update`, `get_state`)
- Schema validation (`validate_event_schema`)

Every agent in the OS depends on it. A syntax error or import failure in kernel.py
breaks all agents simultaneously.

## Proposed Solution

Split into three focused modules, keeping kernel.py as a thin dispatcher:

```
context/
  kernel.py          -- thin CLI dispatcher, imports the three below
  lock_manager.py    -- acquire_lock, release_lock, cleanup_stale_rotate_lock
  event_bus.py       -- emit_event, rotate_log, validate_event_schema
  state_manager.py   -- state_update, get_state, get_lock_timeout
```

`kernel.py` becomes:
```python
from lock_manager import acquire_lock, release_lock
from event_bus import emit_event
from state_manager import state_update, get_state
```

All existing CLI invocations (`python context/kernel.py emit_event ...`) remain unchanged.

## Migration Impact

- All SKILL.md files use `python context/kernel.py <subcommand>` -- no changes needed
- `context/agents.json` unchanged
- `init_agentic_os.py` copies all 4 files instead of 1
- `runtime/` directory gains 3 new files

## Acceptance Criteria

- [ ] All existing `kernel.py` CLI subcommands work identically
- [ ] Each module can be imported independently without circular deps
- [ ] kernel.py is under 50 lines
- [ ] All existing evals pass
