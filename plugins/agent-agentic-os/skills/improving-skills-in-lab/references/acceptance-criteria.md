# Acceptance Criteria: improving-skills-in-lab

Merged verbatim from the retired skills; one section per mode. Headings inside a section are one level deeper than in the original.

## Contents

- [Mode: planner](#mode-planner)
- [Mode: setup](#mode-setup)
- [Mode: log](#mode-log)
- [Mode: backport](#mode-backport)
- [Mode: memory](#mode-memory)

## Mode: planner

### ✅ Scenarios that must trigger
- "I found a new browser automation pattern I want to generalize and apply to my agents"
- "I need an agent that automatically monitors plugin health and flags stale evals, it doesn't exist yet"
- "Run improvement loops on both the `score` mode and running-exploration-cycle at the same time"

### ❌ Scenarios that must NOT trigger
- "Show me what patterns are currently documented in the domain-patterns layer"
- "Show me the current eval score for the `score` mode"
- "List all the agents we currently have in the agentic-os plugin"

## Mode: setup

### ✅ Scenarios that must trigger
- "Set up an eval lab for the link-checker skill"
- "Bootstrap the eval repo for running an autoresearch improvement loop"
- "Prepare the test repo for skill evaluation"
- "Create an isolated eval environment for this skill"

### ❌ Scenarios that must NOT trigger
- "Run the improvement loop on this skill"
- "Backport the lab results to master"
- "Create a new skill from scratch"
- "Optimize this skill using the improvement loop"

## Mode: log

### ✅ Scenarios that must trigger
- "Append the latest evolution verifier results to the experiment log"
- "Query the experiment log for all T2-D failures"
- "Show me a summary of all experiment runs — how many passed vs failed"

### ❌ Scenarios that must NOT trigger
- "Run the evolution verifier on all scenarios"
- "Show me the current eval score for the `plan` mode"

## Mode: backport

### ✅ Scenarios that must trigger
- "backport the lab results from the link-checker test run"
- "review what the lab agent changed in the lab repo"
- "apply the skill improvements from the lab run to master"
- "the lab run is done, check which files were updated"

### ❌ Scenarios that must NOT trigger
- "run the improvement loop on this skill for 10 iterations"
- "fix this bug in the link checker script"
- "deploy the plugin to my local environment"
- "set up a lab repo for this skill"

## Mode: memory

**Version**: 2.0 | **Type**: Quality Assurance Matrix

The `memory` mode must successfully pass the following scenarios.

### ✅ Positive Scenarios (Must Execute Memory Protocol)

1. **Explicit Request**: "Can you summarize the session and save today's memory?" -> Correctly parses log, identifies facts, checks conflicts, appends to `memory.md`, archives log.
2. **Implicit Closure**: "That's it for today, thanks." -> Agent detects end-of-session, transparently runs the memory promotion logic before terminating.
3. **No Promotable Facts**: Session was spent purely running tests that repeatedly failed. -> Agent recognizes no architectural facts occurred, archives log, leaves `memory.md` untouched.
4. **Task Carryover**: "We didn't finish the login script, let's do it tomorrow." -> Agent leaves the login script to-do in a session file instead of promoting it to `memory.md` facts.
5. **Conflict Detected**: Agent attempts to promote "Always use vanilla CSS" but reads `memory.md` and sees "Always use Tailwind". -> Agent immediately halts Write, notifies user of contradiction, and awaits resolution.

### ❌ Negative Scenarios (Must Halt or Fail Cleanly)

1. **Dementia Write**: Agent directly overwrites existing `memory.md` rules with conflicting session facts without prompting the user. (FAIL condition).
2. **Volatile Promotion**: Agent promotes ephemeral error messages or single-use bash commands to `memory.md`. (FAIL condition).
3. **Ghost Append**: Agent appends to `memory.md` but fails to clear/archive the daily session log, causing duplicate processing the next day. (FAIL condition).
