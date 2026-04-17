---
concept: rigorous-benchmarking-grading-loop
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/rigorous-benchmarking-loop.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.014508+00:00
cluster: skill
content_hash: 46c8a1bf8ca41ac7
---

# Rigorous Benchmarking & Grading Loop

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
3. Spawn a Grader subagent to evaluate both outputs against the assertions defined in `./evals.json`.
4. Aggregate the pass rates and resource usage into a `benchmark.json` summary.
```

## Anti-Patterns
- Running tests sequentially when parallel execution is available (wastes user time).
- Eyeballing the results instead of using a programmatic grader or structured assertions.


## See Also

- [[rigorous-benchmarking-loop]]
- [[rigorous-benchmarking-loop]]
- [[rigorous-benchmarking-loop]]
- [[rigorous-benchmarking-loop]]
- [[rigorous-benchmarking-loop]]
- [[rigorous-benchmarking-loop]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/rigorous-benchmarking-loop.md`
- **Indexed:** 2026-04-17T06:42:10.014508+00:00
