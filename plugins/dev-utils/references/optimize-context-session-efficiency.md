# Session Token Efficiency & Delegation Patterns

## Cumulative Cost Dynamics
Token costs compound across turns — every message in a multi-turn session re-pays full context window costs including prior messages, skills, and instruction files.

## Delegation Candidates
| Task Type | Cheap Subagent? | Rationale |
|---|---|---|
| Template filling from input | Yes | No interactive dialogue needed |
| Single-pass document generation | Yes | One-shot, bounded task |
| Data extraction / conversion | Yes | Deterministic execution |
| Multi-turn feedback loops | No | Requires frontier reasoning |
| Architecture / Synthesis | No | High-judgment orchestration |

## Best Practices
1. **Delegate Q&A**: Batch 3-5 clarifying questions into cheap subagent runs rather than bloating the main context.
2. **Compact Regularly**: Run `/compact` between major domain switches.
3. **Pipe Artifacts**: Pass structured markdown files between agents instead of copying conversation transcripts.
4. **Light Orchestration**: Store worker outputs directly to files; bubble only summaries to the parent agent.
