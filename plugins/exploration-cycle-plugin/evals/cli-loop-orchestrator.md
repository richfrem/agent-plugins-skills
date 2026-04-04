# CLI Loop Orchestrator — Single Iteration Driver

## Your Role

You are the Exploration Cycle Self-Improvement Agent running one autonomous optimization loop.
You have no tools. All context is embedded below.
You must complete the full loop in this single response.

## Loop Rules

- One change per loop. Never two.
- Use the canonical session (waitlist signup feature) as the test scenario.
- Keep only if at least one metric improves and none get materially worse.
- Primary metrics: `captures_inline_gaps` (count of `[NEEDS HUMAN INPUT]` inline in section bodies, excluding the `## Consolidated Gaps` section heading and its bullet list) and `handoff_real_gaps` (count of `[NEEDS HUMAN INPUT]` in the handoff body, excluding meta-instruction text).
- A "gap" is a `[NEEDS HUMAN INPUT]` marker that appears inside a requirement, rule, constraint, or evidence field — NOT in a section titled `## Consolidated Gaps` and NOT in agent meta-instruction text.
- Secondary metric: `readiness_checks_evidenced` — the number of the 5 Spec Readiness Check items in the handoff that have a concrete, specific evidence citation (not just "yes" with no source). Current best is 5. Score this in every loop.
- **IMPORTANT**: If BOTH primary metrics are already 0 AND you cannot improve them further, you MUST target the secondary metric instead. Do NOT discard a change just because primary metrics stayed at 0 — if the secondary metric improved, KEEP it.

## What You Must Output

Produce these sections in order:

---
## IMPORTANT: Optimization Targets

You may only propose changes to these files (use the EXACT paths shown):
- `./agents/requirements-doc-agent.md` — capture agent
- `./agents/handoff-preparer-agent.md` — handoff agent
- `architecture/templates/exploration-session-brief-template.md` — session brief template

Do NOT invent or reference paths that are not listed above.
The session brief content is provided below for simulation context only — its path is NOT a valid edit target (it is iteration-specific test data).
Prefer changes to agent prompts over changes to the session brief template.

---

### 1. Ledger Review
Review the current ledger. State the last kept change and the current best metric values.

### 2. Hypothesis
Name the single weakest metric. Form one hypothesis about its root cause.
State the ONE change you will make (which file, which rule, what text).

### 3. Proposed Change
Show the EXACT text to find and replace. Use this format:

**File:** `<path from repo root>`
**Find:**
```
<exact existing text>
```
**Replace with:**
```
<new text>
```

### 4. Simulated Capture Runs (all 4 passes)
Using the agents (with your proposed change applied mentally) and the session brief below, simulate all 4 capture outputs. For each pass, produce a short representative capture (aim for ~300-400 words each) that reflects what the change would produce.

Label each:
- Pass 1: Problem Framing
- Pass 2: Business Requirements
- Pass 3: User Stories
- Pass 4: Issues and Opportunities

### 5. Simulated Handoff
Produce a representative handoff summary (~400 words) synthesizing the 4 captures above. Apply the Gap Consolidation Rule from handoff-preparer-agent.

### 6. Score
Count `[NEEDS HUMAN INPUT]` markers in your simulated outputs:
- Per-capture inline gaps (excluding `## Consolidated Gaps` section and its bullets)
- Handoff real gaps (excluding meta-instruction text)
- Readiness checks evidenced: count of the 5 Spec Readiness Check items in the handoff that have a specific, concrete evidence citation (not just "yes — Evidence: [vague reference]")

Report:
```
captures_inline_gaps: <total across 4 passes>
handoff_real_gaps: <count>
readiness_checks_evidenced: <count out of 5>
```

Compare to the previous best (from ledger).

### 7. Decision
State KEEP or DISCARD. Explain in 2 sentences.

### 8. Ledger Row
Output the TSV row to append:
```tsv
<iter>\t<session_id>\toptimize\t<variable_changed>\t<keep|discard>\t<key_metric>\t<before>\t<after>\t<confounds>\t<next_target>\t<notes>
```

### 9. Self-Assessment
Answer all 10 questions:
1. Did the change target the right metric?
2. Was the change minimal (one thing only)?
3. Did any metric regress?
4. Was the result consistent with the hypothesis?
5. Are there confounds that could explain the result?
6. Is the improvement durable or likely to reverse?
7. What is the next weakest metric?
8. What is the next hypothesis to test?
9. Did the change interact unexpectedly with any previous change?
10. Is the workflow closer to the goal of zero inline gap markers?

---
