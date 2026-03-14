# Rigorous Benchmarking & Grading Loop

**Pattern Name**: Rigorous Benchmarking & Grading Loop
**Category**: Testing & Evaluation
**Complexity Level**: L4 (Advanced Agentic Pattern)

## Description
This pattern treats agent skills like software by enforcing strict unit testing against them. Instead of qualitative "vibes-based" evaluation, it runs parallel subagents using a "With Skill" configuration and a "Baseline" (no skill) configuration. It captures quantitative metrics (token usage, execution time) and uses a dedicated grader subagent to score the outputs based on explicit JSON assertions.

## When to Use
- When developing new, complex agent skills that require high reliability.
- When optimizing an existing skill and needing to prove A/B improvements.
- When the skill produces deterministic or easily verifiable outputs (e.g., file transformations, code generation).

## Implementation Example
```markdown
### Evaluation Loop
1. Spawn two subagents in parallel for each test case:
   - **Baseline**: Prompt without the skill.
   - **With Skill**: Prompt with access to this specific skill.
2. Capture `total_tokens` and `duration_ms` for both runs.
3. Spawn a Grader subagent to evaluate both outputs against the assertions defined in `evals/evals.json`.
4. Aggregate the pass rates and resource usage into a `benchmark.json` summary.
```

## Anti-Patterns
- Running tests sequentially when parallel execution is available (wastes user time).
- Eyeballing the results instead of using a programmatic grader or structured assertions.
