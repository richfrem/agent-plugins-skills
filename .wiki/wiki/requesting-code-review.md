---
concept: requesting-code-review
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/requesting-code-review/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.195102+00:00
cluster: before
content_hash: c1194bad881d4423
---

# Requesting Code Review

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: requesting-code-review
description: Use when completing tasks, implementing major features, or before merging to verify work meets requirements
---

> **Source:** Ported from [obra/superpowers](https://github.com/obra/superpowers) by [Jesse Vincent](https://github.com/obra). Adapted for the `agent-plugins-skills` ecosystem. Original concepts and Iron Laws credit belongs to Jesse.

# Requesting Code Review

Dispatch the `code-reviewer` agent to catch issues before they cascade. The reviewer gets precisely
crafted context for evaluation - never your session's history. This keeps the reviewer focused on
the work product, not your thought process, and preserves your own context for continued work.

**Core principle:** Review early, review often.

## When to Request Review

**Mandatory:**
- After completing a major feature
- Before merge to main
- After each task in multi-task implementation

**Optional but valuable:**
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing complex bug

## How to Request

**1. Get git SHAs:**
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

**2. Dispatch code-reviewer agent:**

Use the Agent tool with subagent_type `code-reviewer`, providing:
- `WHAT_WAS_IMPLEMENTED` - What you just built
- `PLAN_OR_REQUIREMENTS` - What it should do (link to spec or plan)
- `BASE_SHA` - Starting commit
- `HEAD_SHA` - Ending commit
- `DESCRIPTION` - Brief summary of the diff

**3. Act on feedback:**
- Fix Critical issues immediately
- Fix Important issues before proceeding
- Note Minor issues for later
- Push back if reviewer is wrong (with reasoning)

## Example

```
[Just completed: Add verification function]

BASE_SHA=$(git log --oneline | grep "previous task" | head -1 | awk '{print $1}')
HEAD_SHA=$(git rev-parse HEAD)

[Dispatch code-reviewer agent]
  WHAT_WAS_IMPLEMENTED: Verification and repair functions for conversation index
  PLAN_OR_REQUIREMENTS: Task 2 from plan.md - verifyIndex() and repairIndex()
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661
  DESCRIPTION: Added verifyIndex() and repairIndex() with 4 issue types

[Agent returns]:
  Strengths: Clean architecture, real tests
  Issues:
    Important: Missing progress indicators
    Minor: Magic number (100) for reporting interval
  Assessment: Ready to proceed

[Fix progress indicators]
[Continue to next task]
```

## Integration with Workflows

**Multi-task implementation:**
- Review after each task
- Catch issues before they compound
- Fix before moving to next task

**Single feature:**
- Review before merge
- Review when stuck

## Red Flags

**Never:**
- Skip review because "it's simple"
- Ignore Critical issues
- Proceed with unfixed Important issues
- Argue with valid technical feedback

**If reviewer wrong:**
- Push back with technical reasoning
- Show code/tests that prove it works
- Request clarification

## Agent Integration Note

In `agent-agentic-os` with the concurrent-agent-loop pattern, dispatch the code-reviewer
as a PEER_AGENT via the kernel event bus: emit `task.assigned`, receive `task.complete`.
This integrates review into the ORCHESTRATOR/INNER_AGENT/PEER_AGENT topology and makes
review quality a measurable signal in the improvement loop.


## See Also

- [[code-reviewer]]
- [[claude-code-subagents-collection]]
- [[code-reviewer]]
- [[architect-review]]
- [[red-team-review-loop]]
- [[acceptance-criteria-red-team-review]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/requesting-code-review/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.195102+00:00
