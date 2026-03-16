# Delegated Constraint Verification Loop

**Pattern Name**: Delegated Constraint Verification Loop
**Category**: Execution & Safety
**Complexity Level**: L5 (Advanced Agentic Pattern)

## Description
Relying purely on an LLM to self-evaluate its own output quality (e.g., "Check your work to make sure the code runs") is fundamentally flawed; an LLM operating in the same context window will often confidently justify its own hallucinations. This pattern creates a detached, deterministic "Verification Loop" by delegating the evaluation to an external, sandboxed script (like a unit test runner, a linter, or a macro execution engine). The script runs the agent's artifact, captures the specific semantic errors resulting from the execution, and feeds a structured JSON error report back to the agent for correction.

## When to Use
- When the agent is writing code, formulas, or complex configurations that can be definitively proved right or wrong by a compiler/engine.
- When generating files with strict dependencies (like Excel formulas, SQL migrations, or Terraform plans).

## Implementation Example
```markdown
### Verification Protocol
After writing your configuration file, you MUST NOT consider the task complete until you execute the verification script:
1. Run `python scripts/verify_config.py output.yaml`.
2. This script will return JSON. If `"status": "success"`, you may proceed.
3. If `"status": "errors_found"`, the JSON will contain an `error_summary` mapping line numbers to syntax violations. You MUST read this JSON, revise your code to fix the exact line numbers identified, and re-run the script until it passes.
```

## Anti-Patterns
- Telling the agent "Review your code carefully for errors" without providing a deterministic tool to actually execute it.
- Letting the verification tool output massive, unstructured console logs (like a raw traceback) rather than parsing the traceback into a clean JSON summary for the LLM.
