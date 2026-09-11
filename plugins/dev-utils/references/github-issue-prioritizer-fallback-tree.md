# Procedural Fallback Tree: GitHub Issue Prioritizer

## 1. Missing Tier or Blocker Information
- **Condition**: Issue has no `tier:*` or blocker labels.
- **Action**: Assess occurrence frequency; if absent, default rank safely to `P3` (Low Priority).

## 2. Invalid GraphQL Project ID
- **Condition**: GitHub Projects v2 `project_id` or `item_id` format invalid or inaccessible.
- **Action**: Output calculated priority label directly to stdout so priority can be applied via standard issue labels (`gh issue edit --add-label`).
