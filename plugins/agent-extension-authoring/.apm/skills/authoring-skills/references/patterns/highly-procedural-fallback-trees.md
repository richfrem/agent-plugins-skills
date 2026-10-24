# Highly Procedural Fallback Trees

**Pattern Name**: Highly Procedural Fallback Trees
**Category**: Robustness & Error Handling
**Complexity Level**: L4 (Advanced Agentic Pattern)

## Description
For highly brittle, deterministic tasks (like translating PDF coordinates or interacting with legacy systems), relying on an LLM's raw reasoning or trial-and-error can lead to catastrophic cascading failures. This pattern defines a strict, step-by-step fallback hierarchy. It removes agentic discretion in failure modes, explicitly dictating "If A fails, execute B. If B fails, drop to C."

## When to Use
- When a task involves geometric bounds, exact math, or strict proprietary formats.
- When the primary method (e.g., structural extraction) frequently fails silently due to edge cases (e.g., scanned documents).
- When you need to prevent the agent from infinitely looping on a single broken script.

## Implementation Example
```markdown
### Coordinate Extraction Fallback Matrix
1. **Primary (Approach A)**: Attempt to read the form using `extract_form_structure.py`.
2. **Validation**: If `form_structure.json` contains meaningful labels, proceed. If labels are missing or read as `(cid:X)`, ABORT Approach A.
3. **Fallback 1 (Approach B)**: Convert PDF to images using ImageMagick crops to visually estimate boundaries.
4. **Validation Gate**: You MUST run `check_bounding_boxes.py` to ensure no coordinates overlap BEFORE attempting to fill the PDF.
```

## Anti-Patterns
- Writing "Try to extract the coordinates and fix any errors along the way." (Too loose, invites hallucination).
- Allowing destructive or final actions (like writing to the DB or exporting the PDF) without passing a strict validation gate script first.
