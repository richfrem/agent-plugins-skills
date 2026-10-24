# Passive Style Injection Payload

**Pattern Name**: Passive Style Injection Payload
**Category**: State & Knowledge
**Complexity Level**: L4 (Advanced Agentic Pattern)

## Description
Standard agent skills are generally procedural (e.g., "Do X, then Y, then Z"). A **Passive Style Injection Payload** is a non-procedural skill that acts purely as an environmental modifier or contextual dictionary. Instead of teaching the agent *how* to do a task, it provides a highly concentrated, isolated bundle of stylistic rules, design tokens, or specific tone-of-voice constraints. When a user asks the agent to perform a standard generative task (like writing a React component), they can invoke this payload to globally modify the output's aesthetic.

## When to Use
- When multiple different skills in your ecosystem (chart generators, UI builders, presentation makers) all need to adhere to the same corporate branding or visual identity.
- When isolating tone-of-voice or persona rules away from core workflow logic to keep core `././SKILL.md` files lean.

## Implementation Example
```markdown
### Design Token Registry
When asked to apply "Brand Guidelines" to ANY generated code or artifact, you must use the following semantic tokens. DO NOT invent your own colors.

| Token Intent | Hex Code | Tailwind Equivalent | Python RGB Tuple |
|-------------|----------|---------------------|------------------|
| Primary Background | `#faf9f5` | `bg-[#faf9f5]` | `(250, 249, 245)` |
| Primary Accent | `#d97757` | `text-[#d97757]` | `(217, 119, 87)` |

### Syntax Application Rules
- **If generating HTML/CSS**: Map these hex codes to CSS variables in the `:root`.
- **If generating Python Charts**: Map these tuples to a custom Matplotlib `cycler`.
```

## Anti-Patterns
- Hardcoding company-specific hex codes directly inside a procedural script (like a charting tool), which guarantees inconsistency when branding changes.
- Providing hex codes without providing the exact code syntax required to apply them in target languages, leaving the agent to hallucinate the implementation.
