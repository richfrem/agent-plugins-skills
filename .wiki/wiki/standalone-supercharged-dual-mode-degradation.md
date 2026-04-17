---
concept: standalone-supercharged-dual-mode-degradation
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/dual-mode-degradation.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.007295+00:00
cluster: user
content_hash: 26081ba21abdb9b5
---

# Standalone + Supercharged Dual-Mode Degradation

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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


## See Also

- [[dual-mode-degradation]]
- [[dual-mode-degradation]]
- [[dual-mode-degradation]]
- [[dual-mode-degradation]]
- [[dual-mode-degradation]]
- [[dual-mode-degradation]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/dual-mode-degradation.md`
- **Indexed:** 2026-04-17T06:42:10.007295+00:00
