# legacy-system-business-rules

Workflows for discovering, investigating, and codifying business logic. Use this skill to register new Business Rules (BR-XXXX) or consolidate duplicates.

## Workflows

| Command | Purpose |
|---|---|
| `/legacy-system-business-rules_investigate-business-rule` | Search for existing rules before creating new ones |
| `/legacy-system-business-rules_codify-business-rule` | Register and document a new BR-XXXX file |
| `/legacy-system-business-rules_consolidate-business-rules` | Merge duplicate or related rules into a single definition |

## Convention

Always run `investigate-business-rule` before `codify-business-rule` to avoid duplicates.

Business Rules are stored in `legacy-system/business-rules/BR-NNNN-[Slug].md` in the knowledge base.

## References

- `references/diagrams/workflows/business-rule-candidate-discovery.mmd`
