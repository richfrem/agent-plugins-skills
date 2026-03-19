# Root-Cause Category Selection (Anti-Symptom Triage)

**Use Case:** Triage, routing, and classification skills (support tickets, bug reports, feature requests).

## The Core Mechanic

Agents naturally classify based on semantic similarity to user input (e.g., User says "Login button is broken" -> Agent classifies as "Account Issue"). You must explicitly instruct the agent to classify based on the inferred **root cause system failure**, not the surface symptom.

### Implementation Standard

Provide a category disambiguation table in the `SKILL.md` that teaches the agent how to look past symptoms:

```markdown
## Classification Principles (Root Cause > Symptom)

- "Customer can't log in because of a confirmed outage" -> **Infrastructure** (Not Account)
- "It used to work and now it doesn't" -> **Bug** (Not How-To)
- "I want it to work differently" -> **Feature Request** (Not Bug)
- Conflict between Bug and Feature Request -> **Bug is primary**
```

Require the output to separate the symptom from the cause:
```markdown
**Reported Symptom:** [What the user sees]
**Inferred Root Cause Category:** [The underlying system responsible]
```
