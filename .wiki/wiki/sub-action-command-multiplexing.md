---
concept: sub-action-command-multiplexing
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/sub-action-multiplexing.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.016041+00:00
cluster: plugin-code
content_hash: 2355d62fd4994f55
---

# Sub-Action Command Multiplexing

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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


## See Also

- [[sub-action-multiplexing]]
- [[sub-action-multiplexing]]
- [[sub-action-multiplexing]]
- [[sub-action-multiplexing]]
- [[sub-action-multiplexing]]
- [[sub-action-multiplexing]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/sub-action-multiplexing.md`
- **Indexed:** 2026-04-17T06:42:10.016041+00:00
