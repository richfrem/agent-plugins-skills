# L4 Artifact Lifecycle State Machine
**Purpose:** Manage the creation, publication, and deprecation of persistent knowledge.
**Mechanics:**
All durable artifacts (KB articles, standard responses) follow this state flow:
1. **Draft:** Created, pending peer/human review.
2. **Published:** Live and canonical.
3. **Needs Update:** Flagged by decay triggers (e.g. 6-months old, flagged by user workflow).
4. **Archived:** Preserved but inactive (superseded).
5. **Retired:** Deleted/Removed.
