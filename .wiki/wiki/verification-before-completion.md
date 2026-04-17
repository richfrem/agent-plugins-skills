---
concept: verification-before-completion
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/verification-before-completion/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.283206+00:00
cluster: plugin-code
content_hash: 62ece63427a71205
---

# Verification Before Completion

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always
---

> **Source:** Ported from [obra/superpowers](https://github.com/obra/superpowers) by [Jesse Vincent](https://github.com/obra). Adapted for the `agent-plugins-skills` ecosystem. Original concepts and Iron Laws credit belongs to Jesse.

# Verification Before Completion

## Overview

Claiming work is complete without verification is dishonesty, not efficiency.

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

## Red Flags - STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!", etc.)
- About to commit/push/PR without verification
- Trusting agent success reports
- Relying on partial verification
- Thinking "just this once"
- Tired and wanting work over
- **ANY wording implying success without having run verification**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence is not evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter is not the compiler |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion is not an excuse |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**Tests:**
```
OK  [Run test command] [See: 34/34 pass] "All tests pass"
NO  "Should pass now" / "Looks correct"
```

**Regression tests (TDD Red-Green):**
```
OK  Write -> Run (pass) -> Revert fix -> Run (MUST FAIL) -> Restore -> Run (pass)
NO  "I've written a regression test" (without red-green verification)
```

**Build:**
```
OK  [Run build] [See: exit 0] "Build passes"
NO  "Linter passed" (linter does not check compilation)
```

**Requirements:**
```
OK  Re-read plan -> Create checklist -> Verify each -> Report gaps or completion
NO  "Tests pass, phase complete"
```

**Agent delegation:**
```
OK  Agent reports success -> Check VCS diff -> Verify changes -> Report actual state
NO  Trust agent report
```

## Why This Matters

From observed failure patterns:
- Trust broken when claims precede evidence
- Undefined functions shipped - would crash at runtime
- Missing requirements shipped - incomplete features delivered
- Time wasted on false completion then redirect then rework
- Friction events of type `false_completion_claim` accumulate in the improvement ledger

## When To Apply

**ALWAYS before:**
- ANY variation of succ

*(content truncated)*

## See Also

- [[autoresearch-loop-verification-before-completion]]
- [[autoresearch-loop-verification-before-completion]]
- [[delegated-constraint-verification-loop]]
- [[delegated-constraint-verification-loop]]
- [[delegated-constraint-verification-loop]]
- [[delegated-constraint-verification-loop]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/verification-before-completion/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.283206+00:00
