# Output Classification Tagging

**Use Case:** Plugins that generate sensitive content, legal drafts, security audits, or any artifact that requires special handling by downstream systems or users.

## The Core Mechanic

Do not assume the user will remember how to handle the artifact the agent generates. The agent should explicitly tag its own output with handling metadata, effectively acting as an automated data classification system.

### Implementation Standard

Embed a standard classification block at the top or bottom of the output template:

```markdown
### Artifact Classification
- **Sensitivity**: [Public / Internal / Confidential / Restricted]
- **Privilege**: [Attorney-Client Privileged / Work Product / Not Privileged]
- **Status**: [Draft / Final Recommended]
- **Retention**: [Standard / Ephemeral]
```

Instruct the skill to determine these values based on the initial input context (e.g., if the user asked to review an embargoed press release, the sensitivity must be `Restricted`).
