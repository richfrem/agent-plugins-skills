# Priority-Ordered Source Scanning

**Use Case:** Commands that search for entities across multiple systems (e.g., searching for a "Customer" in CRM, Billing, Support, and Email).

## The Core Mechanic

When querying multiple systems, do not treat all systems as equally authoritative. A contract in a CLM system supersedes an off-hand mention in a Slack message. The command must define a strict hierarchy of authority and execute searches in that order.

### Implementation Standard

In the command file, list the search steps in explicit priority order, and instruct the agent to halt or change its confidence if a higher-priority source contradicts a lower-priority one:

```markdown
## Step 2: Cross-System Entity Resolution

Search for the entity across all connected systems in this exact priority order:

1. **~~CLM (Authoritative)** - If found here, treat this as the ground truth name/status.
2. **~~CRM (Primary Context)** - Use for relationship status and account owner.
3. **~~Email (Recency)** - Use only for recent intent signals.
4. **~~Chat (Informal)** - Use only if no other context exists.
```
