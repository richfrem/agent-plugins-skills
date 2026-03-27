# Lifecycle-Aware Knowledge Management

**Use Case:** Skills that produce durable artifacts like documentation, runbooks, templates, or knowledge base articles.

## The Core Mechanic

Treat artifacts not as static files, but as living documents with an explicit state machine and scheduled maintenance. This prevents documentation rot.

### Implementation Standard

1. **Define the State Machine in SKILL.md:**
   ```markdown
   | State | Meaning | Transition Trigger |
   |-------|---------|-------------------|
   | Draft | Created, needs review | — |
   | Published | Live, authoritative | Peer approval |
   | Needs Update | Flagged for revision | Product changes, customer confusion |
   | Archived | Preserved, not active | Superseded or outdated |
   | Retired | Removed | No longer relevant |
   ```

2. **Establish a Feedback Loop:**
   Instruct the agent to look for gaps during normal operations. For example, if a support skill answers a repeated question, it should automatically trigger the creation of a new KB article or flag the existing one as `Needs Update`.
