# Routing taxonomy

| Category | Signals | Usual path |
|---|---|---|
| Pattern abstraction | "found a pattern", "generalize this", "apply X to my agents" | Update |
| Research application | "read a paper", "apply this technique" | Update |
| Lab setup / improvement | "improve X", "stress test", "run N iterations" | Orchestrate |
| Capability gap | "no skill for", "doesn't exist yet" | Create (after audit) |
| Multi-target | "improve several", "in parallel" | One plan and prompt per target, run sequentially |
| System evolution | "tier 3 friction", "state machine refactor" | Out of lab scope: route to the control plane (`work-intake`) if installed |

Confidence: High = 2+ signals for one category. Medium = one signal or minor overlap.
Low = no clear signal or overlap across 2+ categories. At Low, stop and return one targeted
question to `os-lab-agent`; do not audit or dispatch.

Combined requests: handle the primary category first, the secondary one afterwards.
