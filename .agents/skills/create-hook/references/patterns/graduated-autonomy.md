# Graduated Autonomy Routing

**Use Case:** Any workflow that handles tasks of varying risk levels, where low-risk actions can be fully automated but high-risk actions require human oversight.

## The Core Mechanic

Do not simply classify issues (e.g., High vs. Low priority). Classification without action is incomplete. Instead, map the risk classification directly to different **autonomy ceilings** for the agent.

### Implementation Standard

Inside the skill definition, explicitly define what the agent is authorized to do at each classification tier:

```markdown
## Risk Tiers & Routing

| Classification | Agent Authority | Routing Action |
|----------------|-----------------|----------------|
| **GREEN (Low Risk)** | Fully Autonomous | Approve and execute immediately. Do not ask for confirmation. |
| **YELLOW (Medium Risk)** | Semi-Autonomous | Draft the response/action, but flag for human review. Do not execute. |
| **RED (High Risk)** | Deferential | Stop immediately. Escalate to [Role/Team] with a summary of the issue. |
```

When generating the output or proceeding to the next step, the agent must check this table to determine if it is "allowed" to take action based on the tier it assigned.
