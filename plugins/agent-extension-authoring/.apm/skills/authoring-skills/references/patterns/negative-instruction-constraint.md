# Negative Instruction Constraint

**Pattern Name**: Negative Instruction Constraint
**Category**: Output & Contracts
**Complexity Level**: L4 (Advanced Agentic Pattern)

## Description
Standard instructions tell an agent what to do ("Calculate the sum"). However, LLMs have deeply ingrained behavioral biases (like preferring to execute math in Python rather than writing Excel formulas, or preferring to summarize text rather than quote it). A **Negative Instruction Constraint** explicitly identifies the likely behavioral bias and forbids it using highly contrasting, comparative examples (e.g., ❌ WRONG vs ✅ CORRECT) to structurally override the model's default instincts.

## When to Use
- When you know the LLM tends to take an "easier" or "different" path that technically accomplishes the goal but ruins the architectural intent.
- When generating configuration files where typical LLM helpfulness (like adding explanatory comments) breaks the parser.
- When writing Excel formulas or dynamic structural code.

## Implementation Example
```markdown
### CRITICAL: Native Calculation Requirement
**Always use native Excel formulas instead of calculating values in Python and hardcoding them.** 

### ❌ WRONG - Hardcoding Calculated Values
```python
# Bad: Computing growth rate in Python
growth = (df.iloc[-1]['Revenue'] - df.iloc[0]['Revenue']) / df.iloc[0]['Revenue']
sheet['C5'] = growth  # Hardcodes 0.15
```

### ✅ CORRECT - Using Excel Formulas
```python
# Good: Growth rate as Excel formula so the sheet remains dynamic
sheet['C5'] = '=(C4-C2)/C2'
```
```

## Anti-Patterns
- Writing passive guidelines like "Please try to use formulas if possible" which the LLM will easily ignore in favor of its trained biases.
- Forbidding an action without demonstrating the specific code syntax of the approved alternative.
