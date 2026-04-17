---
concept: tool-agnostic-connector-placeholders-category
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/connector-placeholders.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.006385+00:00
cluster: figma
content_hash: 0ac5b32c854d0e45
---

# Tool-Agnostic Connector Placeholders (`~~category`)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Tool-Agnostic Connector Placeholders (`~~category`)

**Use Case:** When a skill needs to interact with external systems (like Figma, Linear, Notion, etc.) but must remain portable and decoupled from specific enterprise tooling choices.

## The Core Mechanic

Never hardcode specific application names (e.g., "Pull from Figma", "Search Confluence") inside a command's workflow logic. Instead, abstract the tool requirement into a broad **category placeholder** prefixed with `~~`.

### Category Examples
- `~~design tool` (Figma, Sketch, Framer)
- `~~user feedback` (Intercom, Zendesk, SurveyMonkey)
- `~~project tracker` (Linear, Jira, Asana)
- `~~knowledge base` (Notion, Confluence, Guru)
- `~~product analytics` (Amplitude, Mixpanel)

### Implementation Standard

In your `././SKILL.md` or `command.md` file, frame all conditional tool logic around the placeholder:

```markdown
## If Connectors Available
If **~~knowledge base** is connected:
- Search the knowledge base for prior user research on this topic.
- Extract the executive summaries and cross-reference with the current findings.
```

The plugin must also include a `CONNECTORS.md` file at its root that maps the categories to actual allowed MCP servers, acting as the dependency injection blueprint.


## See Also

- [[category-semantic-deferred-tool-binding]]
- [[category-semantic-deferred-tool-binding]]
- [[connector-placeholders]]
- [[category-semantic-deferred-tool-binding]]
- [[category-semantic-deferred-tool-binding]]
- [[connector-placeholders]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/connector-placeholders.md`
- **Indexed:** 2026-04-17T06:42:10.006385+00:00
