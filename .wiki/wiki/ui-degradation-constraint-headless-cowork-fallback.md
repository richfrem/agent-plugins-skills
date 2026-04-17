---
concept: ui-degradation-constraint-headless-cowork-fallback
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/ui-degradation-constraint.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.017152+00:00
cluster: pattern
content_hash: 2553dcabe580892e
---

# UI Degradation Constraint (Headless / Cowork Fallback)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# UI Degradation Constraint (Headless / Cowork Fallback)

**Pattern Name**: UI Degradation Constraint
**Category**: Output & Contracts
**Complexity Level**: L4 (Advanced Agentic Pattern)

## Description
Skills that rely on local servers or browsers to render interactive HTML outputs will crash silently when executed by subagents, in headless CI/CD environments, or in remote VMs (like Cowork) where `webbrowser.open()` is blocked. This pattern mandates that any skill popping a UI must explicitly detect environment capabilities (or catch display exceptions) and seamlessly degrade to generating a localized, static HTML artifact on disk.

## When to Use
- When spinning up local web servers to review outputs (`eval-viewer`).
- When generating complex interactive dashboards.
- When scaffolding UI wireframes that need human approval before committing.

## Implementation Example
```markdown
### Visual Viewer Generation
This skill uses a built-in `<script>` server to display results.
- **Primary execution**: Run `generate_review.py` which calls `webbrowser.open(localhost)`.
- **Degradation trigger**: If `webbrowser.Error` is caught OR if the agent is operating as a background subagent (no terminal display attached):
    - DO NOT fail the script.
    - Suppress the server boot. Write `output.html` to the active workspace using the `--static` flag.
    - Provide the exact file path explicitly to the user in the prompt output so they can download or click it asynchronously.
```

## Anti-Patterns
- Assuming the agent is always running in an attended, local desktop IDE with browser access.
- Halting a 30-minute background generation task because the final display step couldn't find a display manager.


## See Also

- [[ui-degradation-constraint]]
- [[ui-degradation-constraint]]
- [[ui-degradation-constraint]]
- [[ui-degradation-constraint]]
- [[ui-degradation-constraint]]
- [[ui-degradation-constraint]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/ui-degradation-constraint.md`
- **Indexed:** 2026-04-17T06:42:10.017152+00:00
