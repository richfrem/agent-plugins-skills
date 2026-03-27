# legacy-system-business-workflows

Workflows for documenting end-to-end business processes (BW-XXXX) that span multiple forms or system components.

## Workflows

| Command | Purpose |
|---|---|
| `/legacy-system-business-workflows_investigate-business-workflow` | Analyze a process to check if it is already documented |
| `/legacy-system-business-workflows_codify-business-workflow` | Create a new BW-XXXX document describing the end-to-end flow |

## Convention

Use this skill for multi-step processes (e.g. "Inmate Intake", "Warrant Verification") rather than atomic logic rules. Atomic rules belong in `legacy-system-business-rules`.

Business Workflows are stored in `legacy-system/business-workflows/BW-NNNN-[Slug].md` in the knowledge base.

## References

- `references/diagrams/workflows/business-workflow-discovery.mmd`
