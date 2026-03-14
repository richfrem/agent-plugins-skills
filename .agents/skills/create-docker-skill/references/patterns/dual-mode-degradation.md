# Standalone + Supercharged Dual-Mode Degradation

**Use Case:** Ensuring a plugin remains fully functional and useful even if the user operates in an environment with no MCP tool connections, while explicitly surface "power user" capabilities if tools *are* connected.

## The Core Mechanic

Agent workflows should never be binary (either requiring a tool or ignoring tools entirely). Every command must be designed to gracefully degrade by offering a "Standalone" fallback path.

### Implementation Standard

1. **The `README.md` Capability Matrix**:
   Explicitly document this degradation to the user before they even execute the plugin.
   ```markdown
   | Capability        | Standalone Mode            | Supercharged With (MCP)              |
   |-------------------|----------------------------|--------------------------------------|
   | Design critique   | Describe or screenshot     | ~~design tool (pull direct)          |
   | UX Writer         | Paste existing copy        | ~~knowledge base (brand voice guide) |
   ```

2. **The Command Execution Router**:
   Inside the command workflow, state the fallback explicitly rather than silently failing when a tool is absent:
   ```markdown
   If a [tool URL] is provided, fetch the live data.
   If no connection is available, ask the user to paste the raw text or upload a screenshot.
   ```
