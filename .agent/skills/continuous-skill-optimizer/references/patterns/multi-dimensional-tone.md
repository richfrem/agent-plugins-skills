# Multi-Dimensional Tone Configuration

**Use Case:** Skills that draft communications on behalf of the user (emails, PRs, support responses, public statements).

## The Core Mechanic

"Be empathetic and professional" is too vague. Tone should be configured as a multi-dimensional matrix, typically intersecting *Situation Type* with *Relationship Stage*.

### Implementation Standard

Embed a tone matrix and strict writing mechanics into the `SKILL.md`:

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
