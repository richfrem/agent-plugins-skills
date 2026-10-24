# L4 Chained Commands / Workflow Graphs
**Purpose:** Convert isolated CLI commands into a navigable UI flow.
**Mechanics:**
Append an "Offer Next Steps" block to the output of command nodes.
Structure:
```markdown
## Offer Next Steps
- "[Action that logically follows]?" -> "I can do this with /[command]."
- "Should I save this output?" -> "I can route to ~~KB_category"
```
