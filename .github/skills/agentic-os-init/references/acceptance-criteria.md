# Acceptance Criteria: agentic-os-init
**Version**: 2.0 | **Type**: Quality Assurance Matrix

The `agentic-os-init` agent/skill must successfully pass the following scenarios.

## ✅ Positive Scenarios (Must Execute Init Protocol)

1. **Fresh Repository**: Agent correctly scaffolds `CLAUDE.md`, `context/`, `skills/`, and `agents/` in an empty directory.
2. **Existing Repository**: Agent detects existing `CLAUDE.md`, uses `Read` to inspect it, and appends the "Agentic OS Harness" section without destroying existing custom rules.
3. **Heartbeat/Status Setup**: Agent correctly scaffolds `context/status.md` and configures the heartbeat cron/loop syntax suitable for the detected environment.
4. **Hook Verification**: Agent creates or merges `hooks.json` mapping `SessionStart` and `PostToolUse` correctly to the internal python scripts.
5. **Post-Init Briefing**: After writing files, agent successfully executes Phase 4, listing what was created and instructing the user on the next immediate step (e.g., populating `status.md`).

## ❌ Negative Scenarios (Must Halt or Fail Cleanly)

1. **Destructive Overwrite**: Agent blindly overwrites a user's critical 500-line `CLAUDE.md` file with the default template. (FAIL condition).
2. **Partial State Crash**: Agent crashes halfway through scaffolding leaving the repo with broken paths, and fails to rollback or complete. (FAIL condition).
