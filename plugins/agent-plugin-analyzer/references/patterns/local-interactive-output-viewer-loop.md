# Local Interactive Output Viewer Loop

**Pattern Name**: Local Interactive Output Viewer Loop
**Category**: Interaction Design & Feedback
**Complexity Level**: L4 (Advanced Agentic Pattern)

## Description
When agents generate complex UI artifacts, code architectures, or multi-file solutions, forcing the user to review raw outputs in their IDE disrupts the cognitive flow. This pattern dictates that before a destructive generation or "final" output save, the agent spins up a local, lightweight Python server (or equivalent) to render the proposed output in a web browser. The viewer includes a feedback text box that captures user iteration requests directly into a local JSON or text file, which the agent then reads for the next iteration.

## When to Use
- When generating visual artifacts (HTML, SVG, Charts).
- When scaffolding entire directory structures where immediate rollback is painful.
- When generating comparative A/B outputs that require side-by-side human evaluation.

## Implementation Example
```markdown
### Scaffold Preview Phase
Instead of writing the generated skill files directly to `<PLUGIN_DIR>/`:
1. Write the proposed file structure and contents to `/tmp/scaffold-preview/`.
2. Execute `python3 scripts/preview_server.py /tmp/scaffold-preview/`.
3. Provide the user the `localhost` link.
4. Instruct the user to leave feedback in the browser viewer and click "Submit".
5. Read `feedback.json` from the preview directory and iterate if necessary. If empty, commit files to final destination.
```

## Anti-Patterns
- Trusting the user to manually verify a 15-file scaffold in their IDE without making mistakes.
- Providing purely text-based (CLI) output reviews for highly visual components.
