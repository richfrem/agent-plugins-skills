# Self-Correction Patterns

Extracted from the Ralph Loop methodology and adapted for Learning Loop Phase VIII.

## Core Insight

> The best agent loops are **self-referential**: each iteration sees its own previous work 
> and autonomously improves. The prompt stays the same; the state changes.

## Application to Learning Loops

Phase VIII (Self-Correction) benefits from iterative refinement:

```
1. Execute task
2. Validate output (tests, linting, manual review)
3. If validation fails → read failure data as input
4. Re-attempt with failure context
5. Repeat until validation passes OR max iterations reached
```

## Writing Good Self-Correction Prompts

### Clear completion criteria
❌ "Fix the code and make it good."
✅ "Fix until: all tests pass, no lint errors, coverage > 80%."

### Incremental goals
❌ "Implement the entire feature."
✅ "Phase 1: data model. Phase 2: API. Phase 3: tests. Each phase validated before next."

### Escape hatches
Always set limits:
- Maximum iterations (prevent infinite loops)
- Timeout per iteration
- "If stuck after N attempts, document what's blocking and suggest alternatives"

## When Self-Correction Works

**Good for:**
- Tasks with automatic verification (tests, linters, type checkers)
- Iterative refinement (getting tests to pass)
- Well-defined success criteria

**Not good for:**
- Tasks requiring human judgment or design decisions
- One-shot operations (deployments, data migrations)
- Tasks with unclear success criteria

## Integration with Learning Loop

```
Phase IV (Audit) ←──── Iterative research refinement
Phase VI (Seal)  ←──── If seal fails, self-correct and retry
Phase VIII (Retro) ←── Core self-correction phase
```

The key principle: **Failures are data.** Each failed attempt informs the next.
