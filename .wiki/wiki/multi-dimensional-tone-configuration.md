---
concept: multi-dimensional-tone-configuration
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/multi-dimensional-tone.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.011169+00:00
cluster: plugin-code
content_hash: 5b8c4d07aaae53b9
---

# Multi-Dimensional Tone Configuration

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Multi-Dimensional Tone Configuration

**Use Case:** Skills that draft communications on behalf of the user (emails, PRs, support responses, public statements).

## The Core Mechanic

"Be empathetic and professional" is too vague. Tone should be configured as a multi-dimensional matrix, typically intersecting *Situation Type* with *Relationship Stage*.

### Implementation Standard

Embed a tone matrix and strict writing mechanics into the `././SKILL.md`:

```markdown
## Tone Configuration

### Axis 1: Situation Type
| Situation | Tone Label | Characteristics |
|-----------|-----------|----------------|
| Routine update | Professional | Clear, concise, friendly |
| Outage | Urgent | Immediate, transparent, actionable |
| Bad news | Candid | Direct, empathetic, solution-oriented |

### Axis 2: Audience Segment
| Segment | Adjustments |
|---------|------------|
| New User | More formal, extra context |
| Established | Warm, direct, reference history |
| Frustrated | High empathy, concrete action plans |

### Writing Mechanics
- **Use active voice** ("We'll investigate" not "This will be investigated")
- **Use absolute dates** ("by Friday Jan 24" not "in a few days")
```


## See Also

- [[multi-dimensional-tone]]
- [[multi-dimensional-tone]]
- [[multi-dimensional-tone]]
- [[multi-dimensional-tone]]
- [[multi-dimensional-tone]]
- [[multi-dimensional-tone]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/multi-dimensional-tone.md`
- **Indexed:** 2026-04-17T06:42:10.011169+00:00
