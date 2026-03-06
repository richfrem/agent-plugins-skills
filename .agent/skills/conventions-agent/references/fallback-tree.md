# Procedural Fallback Tree: Conventions Agent

## 1. Diff Contains Both Style AND Logic Changes
If a review diff mixes formatting violations with functional/architectural changes:
- **Action**: Separate the concerns. Flag style violations only. Explicitly state "Logic changes are out of scope for this review" and recommend the user invoke the appropriate architectural review skill for the functional parts.

## 2. Type Annotation Cannot Be Determined (External Type)
If a Python function parameter type comes from a third-party library with no stub:
- **Action**: Use `Any` as the type hint with a comment explaining the ambiguity (e.g., `# type: ignore[import]`). Report the ambiguous type to the user. Do NOT leave the parameter unannotated.

## 3. Entire File Missing Header (Not Just Function)
If a source file has no purpose header at all:
- **Action**: Add the full header before reviewing any other violations in the file. Do NOT proceed with function-level review until the file header is in place.
