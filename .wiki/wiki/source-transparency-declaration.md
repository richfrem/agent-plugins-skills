---
concept: source-transparency-declaration
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/source-transparency.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.015360+00:00
cluster: agent
content_hash: da621af665404073
---

# Source Transparency Declaration

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Source Transparency Declaration

**Use Case:** Any command that performs research, dependency analysis, or synthesis across multiple systems or files.

## The Core Mechanic

When an agent returns a "Not Found" result, the user does not know if the artifact actually doesn't exist, or if the agent simply failed to check the right systems. A Source Transparency Declaration forces the agent to explicitly report its coverage map before delivering its findings.

### Implementation Standard

Include a mandatory schema block in the `## Output` template of the command file:

```markdown
### Source Transparency
Provide a definitive list of where you looked to generate this report.

- **Sources Checked:** [List the exact tools, databases, or file paths successfully queried]
- **Sources Unavailable:** [List any requested or relevant sources that failed to connect, returned errors, or were skipped]
```

This prevents the agent from confidently claiming "No dependencies found" when its database query silently timed out.


## See Also

- [[source-transparency]]
- [[source-transparency]]
- [[source-transparency]]
- [[source-transparency]]
- [[source-transparency]]
- [[source-transparency]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/source-transparency.md`
- **Indexed:** 2026-04-17T06:42:10.015360+00:00
