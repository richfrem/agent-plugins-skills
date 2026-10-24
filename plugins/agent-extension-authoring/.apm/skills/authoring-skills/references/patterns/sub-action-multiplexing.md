# Sub-Action Command Multiplexing

**Use Case:** A unified domain (e.g., "Design Systems" or "Database Migrations") that requires multiple distinct operations, each with totally different output structures, but which shouldn't pollute the global namespace with a dozen separate slash commands.

## The Core Mechanic

Instead of creating `/audit-design-system`, `/document-component`, and `/extend-pattern`, create a single command namespace (`/design-system`) that multiplexes into distinct sub-action workflows.

### Implementation Standard

1. **Sub-action Documentation**: Use tab-aligned comments in the usage section to define the keywords.
   ```markdown
   ## Usage
   /[command] audit          # Full system audit → score table
   /[command] document       # Component doc → props, a11y, code example
   /[command] extend         # New component → API specs, open questions
   ```

2. **Branching Output Templates**: The single command file must contain multiple completely separate layout contracts. The agent routes to the correct one based on the sub-action suffix:
   ```markdown
   ## Output — Audit action
   [Markdown schema for Audit]

   ## Output — Document action
   [Markdown schema for Documenting a component]
   ```
