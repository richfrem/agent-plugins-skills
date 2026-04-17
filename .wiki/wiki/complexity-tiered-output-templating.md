---
concept: complexity-tiered-output-templating
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/complexity-tiered-output.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.005935+00:00
cluster: plugin-code
content_hash: 515f31b2c43dd181
---

# Complexity-Tiered Output Templating

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Complexity-Tiered Output Templating

**Use Case:** Analytical commands, code generation, or query responses where the user might ask a simple question ("How many rows?") or a complex one ("What is the weekly revenue trend over the past year?").

## The Core Mechanic

Proactively classify the query complexity *before* generating output, and select a fundamentally different output structure (template) based on that tier.

### Implementation Standard

```markdown
## Step 1: Complexity Classification

Analyze the user's request and assign it a tier:

| Tier | Signal | Allowed Output Format |
|------|--------|-----------------------|
| **Quick Answer** | Single metric, simple lookup | Direct Answer + Collapsible Code/Query |
| **Full Analysis** | Trends, multiple variables | Key Finding -> Charts -> Methodology -> Follow-ups |
| **Formal Report** | High-stakes stakeholder query | Exec Summary -> Methodology -> Detailed Findings -> Caveats |

## Step 2: Output Generation

Generate exactly the output format specified for the assigned Tier. Do not mix and match sections.
```


## See Also

- [[complexity-tiered-output]]
- [[complexity-tiered-output]]
- [[complexity-tiered-output]]
- [[complexity-tiered-output]]
- [[complexity-tiered-output]]
- [[complexity-tiered-output]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/complexity-tiered-output.md`
- **Indexed:** 2026-04-17T06:42:10.005935+00:00
