# Planner templates

## Brainstorm prompt

```text
Evolution goal: <goal>
Target: <target skill or agent>
Gaps found by the audit: <list>
Generate exactly 3 distinct approaches. For each: name (2-4 words), what it does (2-3
sentences), what it trades off (1 sentence), effort (Small / Medium / Large).
```

Run it on the cheapest suitable tier listed in the cli-agents model catalog (copilot-models.json).
If no backend is available, write the options yourself and say so.

## Options block (returned in the plan)

```text
Option A - <name> [<effort>]: <description>. Tradeoff: <tradeoff>
Option B - ...
Option C - ...
Recommendation: Option <X> because <one line>.
```

## Task plan

```markdown
# <title>
## Context
## Approach selected (alternatives considered)
## Gaps identified
## Workstreams
| WS | Scope | Files | Order |
## Delegation
## Acceptance criteria
## Status
- [ ] WS-A
```

Ordering rule: structural fixes (model identifiers, path bugs, security flags) are listed
first; additive content (gotchas, handoff blocks, smoke tests) after.

## Delegation prompt

- One section per workstream, with exact file paths and content specification.
- Global instruction: write files directly, do not print delimiters.
- Constraints: paths in SKILL.md are relative to the skill root; no hard-coded model IDs.
- Completion checklist and a COMPLETION_REPORT format. Include an update to
  the plugin map-debt file or evolution log when code or logic changes.
- Self-contained: the delegate has no memory of this session.
