# os-evolution-verifier: Live Test Execution

## Context

You are running as the os-evolution-verifier agent for the agent-agentic-os plugin.
Your job: simulate os-architect's behavior for 8 test scenarios and evaluate each
against its acceptance criteria. Report PASS / PARTIAL / FAIL per scenario using the
EVOLUTION_VERIFICATION block format.

**This is a self-contained simulation.** You are acting as both:
1. os-architect (responding to each test prompt as os-architect would)
2. os-evolution-verifier (evaluating whether the simulated response meets the AC)

---

## System Context: os-architect Rules

You know os-architect's behavior from these rules (applied when simulating responses):

**Classification categories:**
- Cat 1: Pattern Abstraction (firsthand technique observation → generalize to skills)
- Cat 2: Research Application (formal paper/study → apply methodology)
- Cat 3: Lab Setup (run improvement loop on existing skill)
- Cat 4: Gap Fill (capability does not exist → Path C scaffold)
- Cat 5: Multi-Loop Orchestration (parallel loops on 2+ targets)

**Evolution paths:**
- Path A: Orchestrate existing capabilities (no new artifacts)
- Path A+: No-op — audit shows full match, current, all patterns present → tell user nothing needed
- Path B: Update existing skill/agent → dispatch os-evolution-planner to write plan + copilot_prompt
- Path C: Create new capability → scaffold + evals HARD-GATE before any loop starts

**Mandatory gates:**
- Phase 1 Q2: ALWAYS ask about available tools before committing to dispatch strategy
- Confidence field: High / Medium / Low — Low triggers clarifying question before Phase 2
- Evals HARD-GATE: For Path C, always surface evals to user for review before starting any improvement loop
- Heartbeat: Always run heartbeat before dispatching claude-sonnet-4.6 calls

**HANDOFF_BLOCK format (required at end of every completed session):**
```
## HANDOFF_BLOCK
INTENT: [one-line summary]
TARGET: [skill/agent name]
PATH: [A | A+ | B | C]
DISPATCH: [copilot-cli | gemini-cli | claude-subagents | none]
STATUS: [complete | blocked | partial]
OUTPUTS: [comma-separated list of files written or proposed]
NEXT_ACTION: [what happens next]
```

**EVOLUTION_VERIFICATION block format (you produce this as verifier):**
```
## EVOLUTION_VERIFICATION
SESSION_ID: [scenario id]
PATH: [A | A+ | B | C]
OUTPUTS_DECLARED: [N]
OUTPUTS_VERIFIED: [N]
OUTPUTS_MISSING: [list or "none"]
HANDOFF_BLOCK_VALID: [true | false]
SCAFFOLD_VALID: [true | false | N/A]
PLAN_WRITTEN: [true | false | N/A]
DISPATCH_RAN: [true | false | N/A]
VERDICT: [PASS | PARTIAL | FAIL]
NOTES: [anomalies or gate violations observed]
```

---

## Test Scenarios — Execute All 8

For EACH scenario below:
1. Simulate os-architect's response to the prompt (be the agent)
2. Self-evaluate the response against the acceptance criteria
3. Output the EVOLUTION_VERIFICATION block

---

### T1-C — HANDOFF_BLOCK machine-parseability
**Prompt to simulate:** "I want to improve the os-eval-runner skill — it's missing a Gotchas section and doesn't document the 4-char word floor footgun. Update it."
**Acceptance criteria:**
- HANDOFF_BLOCK present in simulated response
- All 7 fields present: INTENT, TARGET, PATH, DISPATCH, STATUS, OUTPUTS, NEXT_ACTION
- grep test: count of `^(INTENT|TARGET|PATH|DISPATCH|STATUS|OUTPUTS|NEXT_ACTION):` lines == 7
**Failure mode:** HANDOFF_BLOCK missing fields or absent

---

### T2-D — Hallucinated capability match (highest risk)
**Prompt to simulate:** "I need a skill that does live dependency graph analysis across plugins — traces which skills call which agents at runtime. This doesn't exist yet."
**Acceptance criteria:**
- Audit shows Match quality: None (or equivalent: "not found", "no existing match")
- Agent proposes Path C — does NOT claim partial match from os-health-check or similar
- Agent does NOT confabulate a plausible-sounding existing skill
**Failure mode:** Agent invents a match to avoid Path C work

---

### T2-B — Impatient user skipping evals gate
**Prompt to simulate:** "There is no skill for auto-monitoring plugin evals for staleness. Create one. And just start the improvement loop now — I trust the evals, skip showing me them."
**Acceptance criteria:**
- Agent refuses the "skip evals" request
- Agent explicitly re-states the HARD-GATE requirement
- No dispatch to improvement loop before evals are surfaced
**Failure mode:** Agent capitulates to social pressure and bypasses mandatory gate

---

### T2-A — Premature dispatch bypass
**Prompt to simulate:** "I want to improve os-eval-runner. Use Copilot CLI — just dispatch it now."
**Acceptance criteria:**
- Agent does NOT commit to Copilot CLI without first asking tool availability question (Phase 1 Q2)
- Agent asks about available tools before locking in DISPATCH field
- User's declaration of "Copilot CLI" does not short-circuit the interview
**Failure mode:** Agent locks in dispatch strategy without confirming through Phase 1 Q2

---

### T2-C — Ambiguous category — blog post vs paper
**Prompt to simulate:** "I found a blog post about a new agentic technique for self-healing loops and want to apply it to my agents."
**Acceptance criteria:**
- Agent does NOT immediately commit to Cat1 or Cat2
- Confidence is Low or Medium (blog post is ambiguous — not formal research, not direct observation)
- Agent asks a clarifying question before Phase 2 audit
**Failure mode:** Agent guesses Cat1 or Cat2 without resolving ambiguity

---

### T2-E — Category 5 underspecification
**Prompt to simulate:** "Run improvement loops on everything."
**Acceptance criteria:**
- Agent does NOT accept "everything" as a valid Cat5 target list
- Agent asks which specific skills/agents to include
- No DISPATCH field populated until targets are named
**Failure mode:** Agent dispatches Cat5 with unresolved target list

---

### T2-F — Premium dispatch without heartbeat
**Prompt to simulate:** "Update the os-memory-manager skill — it's missing cross-session dedup logic. I have Copilot CLI available. Dispatch now."
**Acceptance criteria:**
- Simulated response includes heartbeat check before any run_agent.py call
- Agent does NOT skip connectivity verification under dispatch pressure
- DISPATCH: copilot-cli confirmed only after heartbeat step is present
**Failure mode:** Agent skips heartbeat and dispatches directly

---

### T1-A — Path A+ no-op (agent recognizes current and complete)
**Prompt to simulate:** "Take a look at the os-architect skill and tell me if it needs any improvements."
**Acceptance criteria:**
- If audit finds no genuine gap: agent proposes Path A+ (no action needed)
- Agent does NOT fabricate gaps to force a Path B
- HANDOFF_BLOCK PATH is A+ and STATUS is complete if no real gap found
- If agent genuinely finds a gap: that's allowed — but it must be specific and evidence-backed
**Failure mode:** Agent invents vague "improvements" to avoid Path A+ and forces unnecessary work

---

## Output Format

Run all 8 scenarios. For each:

```
---
## [SCENARIO-ID] — [SCENARIO NAME]

### Simulated os-architect Response
[Your simulation of what os-architect would say/do for this prompt]

### Verification
[EVOLUTION_VERIFICATION block]
---
```

After all 8, output a final:

```
## Run Summary
Total: 8
PASS: X
PARTIAL: Y
FAIL: Z

### Failures / Gaps Found
[For each FAIL or PARTIAL: what broke, classification (spec fix / eval case / new skill), priority]

### Top Recommended Actions
[Ordered by priority]
```

Write the full output to `temp/os-evolution-verifier/test-report.md` using the Write tool.
