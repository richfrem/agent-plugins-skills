# Acceptance Criteria: os-memory-manager
**Version**: 2.0 | **Type**: Quality Assurance Matrix

The `os-memory-manager` must successfully pass the following scenarios.

## ✅ Positive Scenarios (Must Execute Memory Protocol)

1. **Explicit Request**: "Can you summarize the session and save today's memory?" -> Correctly parses log, identifies facts, checks conflicts, appends to `memory.md`, archives log.
2. **Implicit Closure**: "That's it for today, thanks." -> Agent detects end-of-session, transparently runs the memory promotion logic before terminating.
3. **No Promotable Facts**: Session was spent purely running tests that repeatedly failed. -> Agent recognizes no architectural facts occurred, archives log, leaves `memory.md` untouched.
4. **Task Carryover**: "We didn't finish the login script, let's do it tomorrow." -> Agent leaves the login script to-do in a session file instead of promoting it to `memory.md` facts.
5. **Conflict Detected**: Agent attempts to promote "Always use vanilla CSS" but reads `memory.md` and sees "Always use Tailwind". -> Agent immediately halts Write, notifies user of contradiction, and awaits resolution.

## ❌ Negative Scenarios (Must Halt or Fail Cleanly)

1. **Dementia Write**: Agent directly overwrites existing `memory.md` rules with conflicting session facts without prompting the user. (FAIL condition).
2. **Volatile Promotion**: Agent promotes ephemeral error messages or single-use bash commands to `memory.md`. (FAIL condition).
3. **Ghost Append**: Agent appends to `memory.md` but fails to clear/archive the daily session log, causing duplicate processing the next day. (FAIL condition).
