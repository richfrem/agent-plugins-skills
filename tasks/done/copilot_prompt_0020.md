# Copilot Delegation Prompt — Task 0020: os-architect Round-2 Fixes

You are implementing 6 targeted fixes to the os-architect bundle in the
`agent-agentic-os` plugin, identified by a round-2 red-team review.
All files are under `plugins/agent-agentic-os/`.

**CRITICAL RULES**:
- Use the Write tool to write all files directly — do not output markdown delimiters.
- Read each file before editing to preserve surrounding content.
- Do NOT change anything not listed in a workstream spec.
- Workstream order is mandatory: WS-A through WS-F, in order listed.

---

## WS-A — evals.json: Add `expected_category` + Misrouting Risk Cases

**File**: `plugins/agent-agentic-os/skills/os-architect/evals/evals.json`

**Problem**: All 15 cases only test trigger/no-trigger. A prompt routed to Category 3
instead of Category 1 passes the evals. No `expected_category` field; no cases that
test the Cat 1 vs Cat 2 boundary.

**Required changes**:

1. For every `"should_trigger": true` case, add `"expected_category": N` where N is 1–5.
   Map based on the existing intent taxonomy:
   - Prompt 1 (browser automation pattern → generalize): `expected_category: 1`
   - Prompt 2 (karpathy autoresearch → abstract learnings): `expected_category: 1`
   - Prompt 4 (meta-learning paper → apply): `expected_category: 2`
   - Prompt 5 (self-healing research → incorporate): `expected_category: 2`
   - Prompt 7 (improve os-eval-runner, 50 iterations): `expected_category: 3`
   - Prompt 8 (eval lab, deep stress test): `expected_category: 3`
   - Prompt 10 (monitor plugin health, doesn't exist): `expected_category: 4`
   - Prompt 11 (no skill for cross-plugin dependencies): `expected_category: 4`
   - Prompt 13 (loops on os-eval-runner AND exploration-workflow, same time): `expected_category: 5`
   - Prompt 14 (entire pipeline, multiple loops in parallel): `expected_category: 5`

2. For `"should_trigger": false` cases: do NOT add `expected_category`. Leave them as-is.

3. Add 4 misrouting-risk boundary cases at the end (before the closing `]`):

```json
  {"prompt": "I found a Karpathy video showing a new way to train agents — I want to apply that methodology to how we run our improvement loops", "should_trigger": true, "expected_category": 1, "note": "misrouting-risk: Cat1 vs Cat2 — pattern discovery from observed technique, not a formal paper"},
  {"prompt": "I read an ACL paper on reflection-tuning that describes a pattern I want to abstract into a skill", "should_trigger": true, "expected_category": 2, "note": "misrouting-risk: Cat2 vs Cat1 — formal research paper drives the update, not first-hand pattern observation"},
  {"prompt": "Run 10 improvement iterations on exploration-workflow and also set up a new skill for session quality tracking while we're at it", "should_trigger": true, "expected_category": 3, "note": "misrouting-risk: Cat3+Cat4 combined — primary is lab setup; gap fill is secondary, handle sequentially"},
  {"prompt": "I want to get better at writing evals — can you help me understand how the eval runner works?", "should_trigger": false, "note": "misrouting-risk: sounds like Cat3 but is a help/explain request, not an evolution action"}
```

Write the complete updated evals.json using the Write tool.

---

## WS-B — Path Bug: Standardize run_agent.py Path in os-architect-agent.md

**File**: `plugins/agent-agentic-os/agents/os-architect-agent.md`

**Problem**: The Delegation Patterns section uses `.agents/skills/copilot-cli-agent/scripts/run_agent.py`
(the installed path). WS-F (symlink install) is not complete. The working confirmed source
path is `plugins/copilot-cli/scripts/run_agent.py`.

**Required change**: Find EVERY occurrence of:
```
python .agents/skills/copilot-cli-agent/scripts/run_agent.py
```
and replace with:
```
python3 plugins/copilot-cli/scripts/run_agent.py
```

There are exactly 2 occurrences — the heartbeat call and the premium dispatch call.
Edit in place, preserving all surrounding content.

---

## WS-C — Category 5 Phase 3 Dispatch Spec

**File**: `plugins/agent-agentic-os/agents/os-architect-agent.md`

**Problem**: Phase 3 covers Path A/B/C but Category 5 (Multi-Loop Orchestration) has no
dispatch spec. When the user requests parallel improvement loops, the agent has no concrete
instruction, producing hallucinated behavior.

**Required change**: After the Path C block (ending with "Step 8: Invoke os-architect-tester...")
and before the HANDOFF_BLOCK section, add:

```markdown
**Category 5 — Multi-Loop Orchestration**:
- Identify each distinct target from the user's request (one per skill/agent to improve).
- Each target is an independent Path A dispatch — do not merge them into one delegation prompt.
- For each target:
  1. Verify the capability exists (same Phase 2 file-read check as Path A).
  2. Write a separate delegation prompt: `temp/copilot_prompt_<slug>-<target>.md`.
  3. Dispatch to `run_agent.py` sequentially (not in parallel) — one request at a time.
     Premium requests are charged per call; sequential dispatch allows abort-on-failure.
- Report per-target results as each completes. Do not wait for all before reporting.
- If a target doesn't exist (gap), classify that target as Path C and handle separately
  before returning to the remaining Path A dispatches.
- Emit one HANDOFF_BLOCK at the end covering all targets:
  TARGET = comma-separated list, STATUS = running (if any dispatched) or complete.
```

---

## WS-D — os-evolution-planner: Add WS Ordering Rule to Template

**File**: `plugins/agent-agentic-os/skills/os-evolution-planner/SKILL.md`

**Problem**: The "Workstream order matters" constraint is in Gotchas only. The delegation
prompt template in the Output Format section has no ordering instruction. The delegated
agent executing tasks won't see the ordering requirement.

**Required change**: In the Output Format section, after the `## Workstreams` table row
and before the `## Delegation Plan` heading (within the task plan template), add:

```markdown
**WS ordering rule**: Structural fixes (model identifiers, path bugs, security flags) MUST
be listed as the first workstreams. Additive content (Gotchas, HANDOFF_BLOCK, domain
patterns, smoke tests) comes after. The delegated agent executes workstreams in listed order.
```

Also, in the delegation prompt template description (second bullet under Output Format),
add to the list item "One section per workstream with exact file paths and content specs":
append "— listed in order: structural fixes first, then additive content"

---

## WS-E — Confidence-Aware Classification

**Files**:
- `plugins/agent-agentic-os/agents/os-architect-agent.md`
- `plugins/agent-agentic-os/skills/os-architect/SKILL.md`

**Problem**: When a user's request has ambiguous intent (e.g., "improve how we generate
agents and maybe create one"), the agent forces a single category. No confidence signal
means misroutes cascade silently into Phase 2 and Phase 3.

**Required change to `os-architect-agent.md`**: In Phase 1, replace the classification
confirmation block:

OLD:
```
Intent category:    [1-5 and label]
Target:             [skill/agent/gap description]
Available tools:    [copilot-cli / gemini-cli / claude-subagents]
Dispatch strategy:  [derived from tools answer]
```

NEW:
```
Intent category:    [1-5 and label]
Confidence:         [High | Medium | Low]
Secondary intents:  [other categories detected, or "none"]
Target:             [skill/agent/gap description]
Available tools:    [copilot-cli / gemini-cli / claude-subagents]
Dispatch strategy:  [derived from tools answer]
```

Also add this rule immediately after the confirmation block (before the "Does this look right?" prompt):

```
Confidence rules:
- **High**: 2+ signal phrases match one category, no overlap with other categories.
- **Medium**: 1 signal phrase match, or minor overlap with one other category.
- **Low**: No clear signal phrase match, or strong overlap across 2+ categories.

If Confidence is Low: ask one targeted clarifying question before confirming.
Example: "You mentioned both [signal A] and [signal B] — are you primarily looking to
[Category X option] or [Category Y option]?"
Do NOT proceed to Phase 2 until confidence is Medium or High.
```

**Required change to `skills/os-architect/SKILL.md`**: In the smoke test section, add a
4th test case:
```
4. Given "I want to explore improving how we generate agents and maybe create one" →
   agent identifies Low confidence (Cat 3 + Cat 4 overlap), asks clarifying question
   before proceeding to Phase 2
```

---

## WS-F — No-Op Path

**Files**:
- `plugins/agent-agentic-os/agents/os-architect-agent.md`
- `plugins/agent-agentic-os/skills/os-architect/SKILL.md`

**Problem**: When the audit returns Full match + current + self-healing patterns present,
the agent has no "nothing to do" response. Without it, it forces a path where none is
warranted, wasting improvement loop compute.

**Required change to `os-architect-agent.md`**: In Phase 3, before the existing Path A block,
add:

```markdown
**Path A+ — No Action Warranted (capability exists, current, complete)**:
- Trigger when: Existing match = Full, Match quality = Full, AND all self-healing patterns
  present (Gotchas section exists, HANDOFF_BLOCK present, evals ≥ 6 real cases, Smoke Test present).
- Do NOT invoke sub-agents or write delegation prompts.
- Tell the user:
  > "[Target] is already current and complete. The capability is well-maintained — no evolution
  > action is needed at this time. If you have a specific improvement hypothesis, describe it
  > and I'll recheck against that lens."
- Emit HANDOFF_BLOCK with `PATH: A+`, `STATUS: complete`, `NEXT_ACTION: none — no action warranted`.
```

**Required change to `skills/os-architect/SKILL.md`**: In the Dispatch Paths table,
add a row before Path A:

| A+ — No Action | audit shows full match + all patterns present | tell user, no dispatch |

---

## Completion Checklist

After all workstreams are complete, verify:

```
COMPLETION_REPORT
WS-A: evals.json has expected_category on all TP cases + 4 new boundary cases (19 total) — [ ]
WS-B: python3 plugins/copilot-cli/scripts/run_agent.py appears in architect agent (grep confirm) — [ ]
WS-C: "Category 5 — Multi-Loop Orchestration" section exists in Phase 3 — [ ]
WS-D: WS ordering rule appears in Output Format section of os-evolution-planner SKILL.md — [ ]
WS-E: "Confidence:" field appears in Phase 1 classification block — [ ]
WS-F: "Path A+" appears in Phase 3 and Dispatch Paths table — [ ]
All files written via Write tool (no delimiter output) — [ ]
```
