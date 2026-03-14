# Multi-Variant Trigger Optimizer

**Pattern Name**: Multi-Variant Trigger Optimizer
**Category**: Discoverability & Invocation
**Complexity Level**: L4 (Advanced Agentic Pattern)

## Description
A skill is useless if the agent never decides to use it. This pattern automates the optimization of a skill's description. It evaluates the trigger rate against a curated dataset of ~20 realistic queries (split into "should-trigger" and "should-not-trigger"). It uses a train/test data split and an automated loop to repeatedly re-write the `description` string until the triggering accuracy hits a reliable threshold.

## When to Use
- When a skill has overlapping intent with built-in tools or other generic skills.
- As a final step before packaging a skill for distribution.
- When users report a skill is "undertriggering" (the agent isn't invoking it when it should).

## Implementation Example
```markdown
### Trigger Optimization
1. Create `trigger-evals.json` containing 10 positive test queries and 10 negative "near-miss" queries.
2. Split into 60% train and 40% test.
3. Run the optimization loop: Evaluate the current description's trigger rate on the training set.
4. If the score is suboptimal, instruct an extended-thinking subagent to propose a more aggressive/specific description.
5. Re-evaluate on the test set to prevent overfitting. Repeat up to 5 times.
```

## Anti-Patterns
- Using generic, overly simple negative test cases (e.g., "Write a poem" as a negative test for a PDF form skill). Negative cases must be tricky near-misses.
- Testing the description manually with 1 or 2 prompts.
