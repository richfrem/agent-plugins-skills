# Dynamic Specification Fetching

**Pattern Name**: Dynamic Specification Fetching
**Category**: Context Management & Freshness
**Complexity Level**: L4 (Advanced Agentic Pattern)

## Description
Instead of bundling massive, rapidly changing SDK documentation or external specifications directly inside the plugin's `references/` directory (which causes context bloat and rapid obsolescence), this pattern instructs the agent to dynamically fetch the absolute latest documentation from a trusted source (like raw GitHub URLs) at execution time using standard tools like `WebFetch`.

## When to Use
- When building skills that orchestrate or build against external APIs (e.g., MCP servers, cloud SDKs).
- When the specification is known to change frequently.
- When bundling the spec would exceed recommended skill token limits.

## Implementation Example
```markdown
### SDK Reference
Do not rely on your pre-trained knowledge for the MCP SDK, as it changes frequently.
Before writing any implementation code, use the WebFetch tool to pull the latest specification:
`WebFetch(url="https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md")`
Base all your function signatures and schemas on this dynamically fetched document.
```

## Anti-Patterns
- Hardcoding thousands of lines of external API documentation into `././SKILL.md`.
- Suggesting the user manually copy-paste the documentation into the chat.
