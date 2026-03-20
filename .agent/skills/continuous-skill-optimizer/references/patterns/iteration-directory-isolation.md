# Iteration Directory Isolation (Rollback Safety)

**Pattern Name**: Iteration Directory Isolation
**Category**: State Management & Safeties
**Complexity Level**: L4 (Advanced Agentic Pattern)

## Description
When agents act directly on a single working directory (e.g., iteratively writing code into `src/`), rolling back mistaken generations becomes impossible without `git reset`. This pattern mandates that generation processes save their outputs into inherently isolated, sequentially numbered sibling directories (`iteration-1/`, `iteration-2/`).

## When to Use
- When generating complex multi-file structures iteratively.
- When performing rigorous A/B blind benchmarking where the baseline must be preserved alongside the modified output.
- When scaffolding architectures where user answers to interactive menus frequently change mid-stream.

## Implementation Example
```markdown
### Isolated Scaffolding Protocol
- Do NOT output directly into the final `target/` directory during active iteration.
- Create `/workspace/iteration-1/`. Generate outputs there.
- When the user requests a change, generate outputs into `/workspace/iteration-2/`.
- Once the user explicitly approves an iteration, run a final operational sync script to mirror the chosen iteration to the production `target/` directory.
```

## Anti-Patterns
- Overwriting existing files during generation without explicit confirmation or isolated backup.
- Forcing the user to manually clean up half-generated or hallucinated files if an iteration loop fails.
