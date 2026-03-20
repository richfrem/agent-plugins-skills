# Explicit Seed-Anchored Determinism

**Pattern Name**: Explicit Seed-Anchored Determinism
**Category**: State & Knowledge
**Complexity Level**: L4 (Advanced Agentic Pattern)

## Description
When generating creative, randomized, or chaotic outputs (such as creative writing alternatives, randomized mock data, or algorithmic art), agents naturally produce completely unrepeatable results on subsequent runs. This pattern forces the agent to explicitly anchor its random functions and noise generation to a persistent numerical or string Seed. Even if the output is chaotic, it becomes 100% mathematically deterministic for any given seed.

## When to Use
- Whenever the plugin generates randomized or probabilistic outputs.
- When creating interactive explorers where a user might want to bookmark or share a specific "chaos state".
- When generating synthetic test data where regressions need to be tracked.

## Implementation Example
```markdown
### State Architecture: Deterministic Rendering
The generative algorithms you create must NEVER be truly random. 
1. Always establish a persistent `seed` variable derived from the user's input or randomly generated AT THE START of the session.
2. You must exclusively use seeded random functions (e.g., `randomSeed(seed)`, `srand()`, or Python's `random.seed()`) before generating any values.
3. Display the current Seed integer prominently in the Output Render so the user can recreate this exact execution branch later.
```

## Anti-Patterns
- Using truly random libraries (`Math.random()`, `/dev/urandom`) when generating artifacts that users might want to iterate on.
- Failing to expose the internal seed integer back to the user, effectively trapping the generated variation.
