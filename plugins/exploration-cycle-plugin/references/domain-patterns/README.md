# Domain Patterns — Exploration Cycle

Curated library of known failure types and escape strategies for the exploration workflow.
Each file covers one workflow stage and documents mutations that have produced confirmed improvements.

## What domain patterns are

When the exploration-optimizer encounters a failure type it has seen before, it can apply
a proven escape strategy instead of generating a fresh hypothesis from scratch.

## When to read them

Check this directory during any exploration-optimizer run before formulating a hypothesis.
If the current failure type matches a known pattern, apply that pattern's escape first.

## How to contribute a new pattern

1. A novel friction point occurs and resolves in a confirmed improvement.
2. After a **2nd confirmation** on the same failure type, promote to `## Known Patterns`.
3. Include: failure type, root cause, escape steps, and confirmation count.

## File naming convention

`<stage>.md` — named by the exploration stage where the failure occurs:

| File | Covers |
|:-----|:-------|
| `exploration-session.md` | Session type misclassification, HARD-GATE bypasses, premature handoffs |
| `requirements-capture.md` | BRD quality issues, gap marker inconsistencies, coverage failures |
| `prototype-build.md` | Component decomposition failures, brownfield conflicts, plugin-mode detection |
