# Client-Side Compute Sandbox Constraint

**Pattern Name**: Client-Side Compute Sandbox Constraint
**Category**: Execution & Safety
**Complexity Level**: L5 (Advanced Security Pattern)

## Description
When an agent writes code intended to be executed in an untrusted or client-side environment (such as an exported HTML artifact or an un-sandboxed browser session), it is prone to hallucinate infinite loops, runaway recursion, or mathematically exploding data structures. This pattern enforces a strict, hard-coded execution wrapper or finite upper-bound constraint in the generated code itself to guarantee it cannot spiral into a Denial of Service (DoS) condition or freeze the host application.

## When to Use
- Whenever the agent generates artifacts containing `<script>` tags, Python executables, or WASM destined to run on the user's machine without a dedicated VM container.
- When generating algorithmic art, simulations, or recursive data structures based on user prompts.

## Implementation Example
```markdown
### Security Requirement: Rendering Sandbox
Do not trust user input regarding particle counts, array sizes, or loop lengths.
You MUST enforce the following hard limits inside your generated Javascript code:
1. `const MAX_ENTITIES = 10000;` - If the parameter exceeds this, clamp it.
2. `const MAX_RECURSION_DEPTH = 6;` - All recursive functions must take a depth argument and explicitly `return` if it hits this limit.
3. Every `while` loop must include an explicit safety counter (`let safety_it = 0; while (condition && safety_it < 50000)`)
```

## Anti-Patterns
- Instructing the LLM to write a "complex simulation" without mandating numerical upper bounds in the code.
- Assuming the LLM will naturally write optimized `O(1)` or `O(n)` algorithms.
